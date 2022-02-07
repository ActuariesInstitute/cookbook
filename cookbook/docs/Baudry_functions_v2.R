

library(knitr)
library(rmdformats)
library(data.table)
library(magrittr)
library(lubridate)
library(ggplot2)
library(cowplot)
library(repr)
library(kableExtra)


simulate_central_scenario <- function(seed = 1234){
  
  #seed = 1234  
  set.seed(seed)
  
  # Policy data
  #~~~~~~~~~~~~~~~~~
  
  # polices sold between start 2016 to end 2017
  dt_policydates <- data.table(date_UW = seq(as.Date("2016/1/1"), as.Date("2017/12/31"), "day"))
  
  # number of policies per day follows Poisson process with mean 700 (approx 255,500 pols per annum)
  dt_policydates[, ':='(policycount = rpois(.N,700),
                        date_lapse = date_UW %m+% years(1),
                        expodays = as.integer(date_UW %m+% years(1) - date_UW),
                        pol_prefix = year(date_UW)*10000 + month(date_UW)*100 + mday(date_UW))]
  
  
  # Add columns defining Policy Covers   
  dt_policydates[, Cover_B := round(policycount * 0.25)]
  dt_policydates[, Cover_BO := round(policycount * 0.45)]
  dt_policydates[, Cover_BOT := policycount - Cover_B - Cover_BO]
  
  
  # repeat rows for each policy by UW-Date
  dt_policy <- dt_policydates[rep(1:.N, policycount),c("date_UW", "pol_prefix"), with = FALSE][,pol_seq:=1:.N, by=pol_prefix]
  
  # Create a unique policy number 
  dt_policy[, pol_number := as.character(pol_prefix * 10000 + pol_seq)]
  
  # set join keys
  setkey(dt_policy,'date_UW')
  setkey(dt_policydates,'date_UW')  
  
  # remove pol_prefix before join
  dt_policydates[, pol_prefix := NULL]  
  
  # join cover from summary file (dt_policydates)
  dt_policy <- dt_policy[dt_policydates]  
  
  # now create Cover field for each policy row
  dt_policy[,Cover := 'BO']
  dt_policy[pol_seq <= policycount- Cover_BO,Cover := 'BOT']
  dt_policy[pol_seq <= Cover_B,Cover := 'B']  
  
  # remove interim calculation fields
  dt_policy[, ':='(pol_prefix = NULL,
                   policycount = NULL,
                   pol_seq = NULL,
                   Cover_B = NULL,
                   Cover_BOT = NULL,
                   Cover_BO = NULL)]
  
  # Add remaining policy details
  dt_policy[, Brand := rep(rep(c(1,2,3,4), c(9,6,3,2)), length.out = .N)]
  dt_policy[, Base_Price := rep(rep(c(600,550,300,150), c(9,6,3,2)), length.out = .N)]
  
  # models types and model cost multipliers
  for (eachBrand in unique(dt_policy$Brand)) {
    dt_policy[Brand == eachBrand, Model := rep(rep(c(3,2,1,0), c(10, 7, 2, 1)), length.out = .N)]
    dt_policy[Brand == eachBrand, Model_mult := rep(rep(c(1.15^3, 1.15^2, 1.15^1, 1.15^0), c(10, 7, 2, 1)), length.out = .N)]
  }
  
  dt_policy[, Price := ceiling (Base_Price * Model_mult)]
  
  
  # colums to keep
  cols_policy <- c("pol_number",
                   "date_UW",
                   "date_lapse",
                   "Cover",
                   "Brand",
                   "Model",
                   "Price")
  
  dt_policy <- dt_policy[, cols_policy, with = FALSE]
  
  # check output
  #head(dt_policy)
  
  #save(dt_policy, file = "./dt_policy.rda")
  
  
  # Claims data
  #~~~~~~~~~~~~~~~~~
  
  # All policies have breakage cover
  # claims uniformly sampled from policies
  claim <- sample(nrow(dt_policy), size = floor(nrow(dt_policy) * 0.15))
  
  # Claim serverity multiplier sampled from beta distn
  dt_claim <- data.table(pol_number = dt_policy[claim, pol_number],
                         claim_type = 'B',
                         claim_count = 1,
                         claim_sev = rbeta(length(claim), 2,5))
  
  # identify all policies with Oxidation cover
  cov <- which(dt_policy$Cover != 'B')
  
  # sample claims from policies with cover
  claim <- sample(cov, size = floor(length(cov) * 0.05))
  
  # add claims to table 
  dt_claim <- rbind(dt_claim,
                    data.table(pol_number = dt_policy[claim, pol_number],
                               claim_type = 'O',
                               claim_count = 1,
                               claim_sev = rbeta(length(claim), 5,3)))
  
  
  # identify all policies with Theft cover
  # for Theft claim frequency varies by Brand
  # So need to consider each in turn...
  
  for(myModel in 0:3) {
    
    cov <- which(dt_policy$Cover == 'BOT' & dt_policy$Model == myModel)
    claim <- sample(cov, size = floor(length(cov) * 0.05*(1 + myModel)))
    
    dt_claim <- rbind(dt_claim,
                      data.table(pol_number = dt_policy[claim, pol_number],
                                 claim_type = 'T',
                                 claim_count = 1,
                                 claim_sev = rbeta(length(claim), 5,.5)))
  }
  
  # set join keys
  setkey(dt_policy, pol_number)
  setkey(dt_claim, pol_number)
  
  #join Brand and Price from policy to claim
  dt_claim[dt_policy,
           on = 'pol_number',
           ':='(date_UW = i.date_UW,
                Price = i.Price,
                Brand = i.Brand)]
  
  # use lubridate %m+% date addition operator 
  dt_claim[, date_lapse := date_UW %m+% years(1)]
  dt_claim[, expodays := as.integer(date_lapse - date_UW)]
  dt_claim[, occ_delay_days := floor(expodays * runif(.N, 0,1))]
  
  dt_claim[ ,delay_report := floor(365 * rbeta(.N, .4, 10))]  
  dt_claim[ ,delay_pay := floor(10 + 40* rbeta(.N, 7,7))]  
  
  dt_claim[, date_occur := date_UW %m+% days(occ_delay_days)]
  dt_claim[, date_report := date_occur %m+% days(delay_report)]
  dt_claim[, date_pay := date_report %m+% days(delay_pay)]
  
  dt_claim[, claim_cost := round(Price * claim_sev)]
  
  dt_claim[, clm_prefix := year(date_report)*10000 + month(date_report)*100 + mday(date_report)]
  
  dt_claim[, clm_seq := seq_len(.N), by = clm_prefix]
  dt_claim[, clm_number := as.character(clm_prefix * 10000 + clm_seq)]
  
  # keep only first claim against policy (competing hazards)
  setkeyv(dt_claim, c("pol_number", "clm_prefix"))
  dt_claim[, polclm_seq := seq_len(.N), by = .(pol_number)]
  dt_claim <- dt_claim[polclm_seq == 1,]
  
  
  # colums to keep
  cols_claim <- c("clm_number",
                  "pol_number",
                  "claim_type",
                  "claim_count",
                  "claim_sev",
                  "date_occur",
                  "date_report",
                  "date_pay",
                  "claim_cost")
  
  dt_claim <- dt_claim[, cols_claim, with = FALSE]
  
  output <- list()
  output$dt_policy <- dt_policy
  output$dt_claim <- dt_claim
  
  return(output)
  
}


join_policy_claim <- function(dt_PhoneData,
                              date_pol_start = "date_UW",
                              date_pol_end = "date_lapse",
                              date_occur = "date_occur")
{
  
  # #debug
  # #~~~~~~~~~
   date_pol_start = "date_UW"
   date_pol_end = "date_lapse"
   date_occur = "date_occur"
  # #~~~~~~~~~
  
  dt_policy <- dt_PhoneData$dt_policy
  dt_claim <- dt_PhoneData$dt_claim 
  
  setnames(dt_policy, c(date_pol_start, date_pol_end), c('date_pol_start', 'date_pol_end'),skip_absent=TRUE)
  
  # set policy start and end dates in foverlap friendly format
  dt_policy[, date_pol_start:= floor_date(date_pol_start, unit= "second")]
  dt_policy[, date_pol_end:= floor_date(date_pol_end, unit= "second") - 1]
  
  # create a dummy end claim occurrence date for foverlap
  dt_claim[, date_occur:= floor_date(date_occur, unit= "second")]
  dt_claim[, date_occur_end:= date_occur]
  dt_claim[, date_report:= floor_date(date_report, unit= "second")]
  dt_claim[, date_pay:= floor_date(date_pay, unit= "second")]
  
  # set keys for claim join (by policy and dates)
  setkey(dt_claim, pol_number, date_occur, date_occur_end)
  setkey(dt_policy, pol_number, date_pol_start, date_pol_end)
  
  # use foverlaps to attach claim to right occurrence period and policy
  dt_polclaim <- foverlaps(dt_policy, dt_claim, type="any") ## return overlap indices
  dt_polclaim[, date_occur_end := NULL]
  
  #clean up NA values
  #~~~~~~~~~~~~~~~~~~~~~~~~
  #set NA dates to 31/12/2999
  lst_datefields <- grep(names(dt_polclaim),pattern = "date", value = TRUE)
  
  for (datefield in lst_datefields)
    set(dt_polclaim,which(is.na(dt_polclaim[[datefield]])),datefield,as_datetime("2199-12-31 23:59:59 UTC"))
  
  #set other NAs to zero (claim counts and costs)
  for (field in c("claim_count", "claim_sev", "claim_cost"))
    set(dt_polclaim,which(is.na(dt_polclaim[[field]])),field,0)
  
  #tidy exposures
  dt_polclaim[, ExpoDays:= ceiling((as.numeric(date_pol_end) -     as.numeric(date_pol_start))/(24*60*60))]
  dt_polclaim <- dt_polclaim[ExpoDays > 0]
  
  
  return(dt_polclaim)
}


time_slice_polclaim <- function(dt_polclaim, lst_Date_slice = NULL)
{
  # Time slice Policy & claims 
  
  if (is.null(lst_Date_slice)){
    lst_Date_slice <- floor_date(seq(as.Date("2016/1/1"), as.Date("2019/06/30"), by = 30), unit= "second")     
  }
  
  for (i in 1:length(lst_Date_slice)){
    dt_polclaim[date_pay<= lst_Date_slice[i], paste0('P_t_', format(lst_Date_slice[i], "%Y%m%d")):= claim_cost]
    set(dt_polclaim,which(is.na(dt_polclaim[[paste0('P_t_', format(lst_Date_slice[i], "%Y%m%d"))]])),paste0('P_t_', format(lst_Date_slice[i], "%Y%m%d")),0)
  }
  
  # sort data by policynumber
  setkey(dt_polclaim, pol_number)
}


RBNS_Train_ijk <- function(dt_policy_claim, date_i, j_dev_period, k, reserving_dates, model_vars) {
  
  # # debugging
  # #~~~~~~~~~~~~~
  # dt_policy_claim = dt_polclaim
  # date_i = t_i
  # j_dev_period = 1
  # k = 1
  # reserving_dates = lst_Date_slice
  # #~~~~~~~~~~~~~
  #   
  
  date_i <- as.Date(date_i)
  date_k <- (reserving_dates[which(reserving_dates == date_i) - k + 1])
  date_j <- (reserving_dates[which(reserving_dates == date_k) - j_dev_period])
  
  #i - j - k + 1 (predictor as at date)
  date_lookup <- (reserving_dates[which(reserving_dates == (date_i)) - j_dev_period -k + 1]) 
  
  #i - k to calculate target incremental paid
  target_lookup <- (reserving_dates[which(reserving_dates == (date_i)) - k]) 
  
  #i -k + 1 to calculate target incremental paid
  target_lookup_next <- (reserving_dates[which(reserving_dates == (date_i)) - k + 1]) 
  
  #definition of reported but not settled
  dt_policy_claim <- dt_policy_claim[(date_report <= date_lookup) & (date_pay > date_lookup)] 
  
  #simulated data assumes one payment so just need to check date paid in taget calc
  dt_policy_claim[, ':='(date_lookup = date_lookup,
                         delay_train = as.numeric(date_lookup - date_pol_start), #extra feature
                         j = j_dev_period,
                         k = k,
                         target = ifelse(date_pay<=target_lookup,0,ifelse(date_pay<=target_lookup_next,claim_cost,0)))]
  
  return(dt_policy_claim[, model_vars, with = FALSE])
}


RBNS_Test_ijk <- function(dt_policy_claim, date_i,j_dev_period, k, reserving_dates, model_vars) {
  
  # # debugging
  # #~~~~~~~~~~~~~
  # dt_policy_claim = dt_polclaim
  # date_i = t_i
  # j_dev_period = 1
  # k = 1
  # reserving_dates = lst_Date_slice
  # #~~~~~~~~~~~~~
  #   
  date_i <- as.Date(date_i)
  
  #i - j - k + 1 (predictor as at date)
  date_lookup <- (reserving_dates[which(reserving_dates == (date_i))]) 
  
  #i - k to calculate target incremental paid
  target_lookup <- (reserving_dates[which(reserving_dates == (date_i)) +j_dev_period - 1]) 
  
  #i -k + 1 to calculate targte incremental paid  
  target_lookup_next <- (reserving_dates[which(reserving_dates == (date_i)) + j_dev_period]) 
  
  #definition of reported but not settled
  # P_te_RBNS rowids of policies needing an RBNS reserve
  dt_policy_claim <- dt_policy_claim[date_report <= date_lookup & date_lookup < date_pay] 
  
  #model assumes one payment so just need to check date paid
  dt_policy_claim[, ':='(date_lookup = date_lookup,
                         delay_train = as.numeric(date_lookup - date_pol_start), #extra feature
                         j = j_dev_period,
                         k = k,
                         target = ifelse(date_pay<=target_lookup,0,ifelse(date_pay<=target_lookup_next,claim_cost,0)))] 
  
  return(dt_policy_claim[, model_vars, with = FALSE])
  
}



RBNS_Train <- function(dt_policy_claim, date_i, i, k, reserving_dates, model_vars) {
  # Create a combined TRAIN dataset across all k and j combos
  for (k in 1:k){
    if (k==1) dt_train <- NULL
    for (j in 1:(i - k + 1)){
      dt_train <- rbind(dt_train, RBNS_Train_ijk(dt_polclaim, date_i, j, k,reserving_dates, model_vars))
    }
  }  
  return(dt_train)
}




RBNS_Test <- function(dt_policy_claim, date_i, delta, k, reserving_dates, model_vars) {
  
  # Create a combined TEST dataset across all k and j combos
  for (k in 1:k){
    if (k==1) dt_test <- NULL
    for (j in 1:(delta - k + 1)){
      dt_test <- rbind(dt_test, RBNS_Test_ijk(dt_polclaim, date_i, j, k,reserving_dates, model_vars))
    }
  }
  
  return(dt_test)
}





IBNR_Freq_Train_ijk <- function(dt_policy_claim, date_i, j_dev_period, k, reserving_dates, model_vars, verbose = FALSE) {
  
  # # debugging
  # #~~~~~~~~~~~~~
  # dt_policy_claim = dt_polclaim
  # date_i = t_i
  # j_dev_period = 1
  # k = 1
  # reserving_dates = lst_Date_slice
  # model_vars <- IBNR_model_vars
  # #~~~~~~~~~~~~~
  
  date_i <- as.Date(date_i)
  date_k <- (reserving_dates[which(reserving_dates == date_i) - k + 1])
  date_j <- (reserving_dates[which(reserving_dates == date_k) - j_dev_period])
  date_lookup <- (reserving_dates[which(reserving_dates == (date_i)) - j_dev_period -k + 1]) #i - j - k + 1 (predictor as at date)
  target_lookup <- (reserving_dates[which(reserving_dates == (date_i)) - k]) #i - k to calculate target incremental paid
  target_lookup_next <- (reserving_dates[which(reserving_dates == (date_i)) - k + 1]) #i -k + 1 to calculate targte incremental paid
  
  if(verbose) cat(paste("Valn date", date_i, ", j = ", j_dev_period, ", k =", k, "\n"))
  
  dt_policy_claim <- dt_policy_claim[date_pol_start < date_lookup  & date_lookup < date_report] #definition of IBNR
  
  dt_policy_claim[, ':='(date_lookup = date_lookup,
                         delay_train = as.numeric(date_lookup - date_pol_start), #extra feature
                         j = j_dev_period,
                         k = k,
                         exposure = round((pmin(as.numeric(as.numeric(date_pol_end)), as.numeric(floor_date(date_i, unit= "second")))
                                           - as.numeric(date_pol_start))/(24*60*60*365), 3),
                         target = ifelse(target_lookup <= date_pay &  date_pay< target_lookup_next & date_occur <= date_lookup ,1,0))]
  
  dt_policy_claim <- dt_policy_claim [,.(exposure = sum(exposure)), by= c(setdiff(model_vars, 'exposure')) ]
  
  return(dt_policy_claim[, model_vars, with = FALSE])
  
}



IBNR_Loss_Train_ijk <- function(dt_policy_claim, date_i, j_dev_period, k, reserving_dates, model_vars, verbose = FALSE) {
  
  
  # # debugging
  # #~~~~~~~~~~~~~
  # dt_policy_claim = dt_polclaim
  # date_i = t_i
  # j_dev_period = 1
  # k = 1
  # reserving_dates = lst_Date_slice
  # model_vars <- IBNR_model_vars
  # #~~~~~~~~~~~~~
  
  date_i <- as.Date(date_i)
  date_k <- (reserving_dates[which(reserving_dates == date_i) - k + 1])
  date_j <- (reserving_dates[which(reserving_dates == date_k) - j_dev_period])
  date_lookup <- (reserving_dates[which(reserving_dates == (date_i)) - j_dev_period -k + 1]) #i - j - k + 1 (predictor as at date)
  target_lookup <- (reserving_dates[which(reserving_dates == (date_i)) - k]) #i - k to calculate target incremental paid
  target_lookup_next <- (reserving_dates[which(reserving_dates == (date_i)) - k + 1]) #i -k + 1 to calculate targte incremental paid
  
  if(verbose) cat(paste("Valn date", date_i, ", j = ", j_dev_period, ", k =", k, "\n"))
  
  dt_policy_claim <- dt_policy_claim[(date_lookup < date_report) & (date_occur < date_lookup) & (target_lookup >= date_pay  & date_pay < target_lookup_next)] #definition of reported but not settled
  dt_policy_claim[, ':='(date_lookup = date_lookup,
                         delay_train = as.numeric(date_lookup - date_pol_start), #extra feature
                         j = j_dev_period,
                         k = k,
                         exposure = 1, #all claims trated equal
                         
                         target = ifelse(target_lookup >= date_pay & date_pay < target_lookup_next,claim_cost,0) #model assumes one payment so just need to check date paid
                         
  )]
  
  return(dt_policy_claim[, model_vars, with = FALSE])
}


IBNR_Test_ijk <- function(dt_policy_claim, date_i,j_dev_period, k, reserving_dates, model_vars, verbose = FALSE) {
  
  ## debugging
  ##~~~~~~~~~~~~~
  #dt_policy_claim = dt_polclaim
  #date_i = t_i
  #j_dev_period = 8
  #k = 1
  #reserving_dates = lst_Date_slice
  #model_vars <- IBNR_model_vars
  ##~~~~~~~~~~~~~
  
  date_i <- as.Date(date_i)
  date_lookup <- (reserving_dates[which(reserving_dates == (date_i))]) #i - j - k + 1 (predictor as at date)
  target_lookup <- (reserving_dates[which(reserving_dates == (date_i)) +j_dev_period - 1]) #i - k to calculate target incremental paid
  target_lookup_next <- (reserving_dates[which(reserving_dates == (date_i)) + j_dev_period]) #i -k + 1 to calculate targte incremental paid  
  
  if(verbose) cat(paste("Valn date", date_i, ", j = ", j_dev_period, ", k =", k, "\n"))
  
  # P_te_IBNR rowids of policies needing an RBNS reserve
  dt_policy_claim <- dt_policy_claim[date_pol_start <= date_lookup & date_lookup < date_report] #IBNR
  
  dt_policy_claim[, ':='(date_lookup = date_lookup,
                         delay_train = as.numeric(date_lookup - date_pol_start), #extra feature
                         j = j_dev_period,
                         k = k,
                         exposure = round((pmin(as.numeric(as.numeric(date_pol_end)), as.numeric(floor_date(date_i, unit= "second")))
                                           - as.numeric(date_pol_start))/(24*60*60*365),3),
                         target = ifelse(target_lookup <= date_pay &  date_pay < target_lookup_next & date_occur <= date_lookup ,claim_cost,0))]  #model assumes one payment so just need to check date paid
  
  dt_policy_claim <- dt_policy_claim [,.(exposure = sum(exposure)), by= c(setdiff(model_vars, 'exposure')) ]
  
  return(dt_policy_claim[, model_vars, with = FALSE])
  
}



IBNR_Train <- function(dt_policy_claim, date_i, i, k, reserving_dates, model_vars, verbose = FALSE) {
  
  # Create a combined TRAIN dataset across all k and j combos
  for (k in 1:k){
    if (k==1){
      dt_train_Freq <- NULL
      dt_train_Loss <- NULL
    }
    
    for (j in 1:(i - k + 1)){
      dt_train_Freq <- rbind(dt_train_Freq, IBNR_Freq_Train_ijk(dt_policy_claim, date_i, j, k,reserving_dates, model_vars, verbose))
      dt_train_Loss <- rbind(dt_train_Loss, IBNR_Loss_Train_ijk(dt_policy_claim, date_i, j, k,reserving_dates, model_vars, verbose))
    }
  }
  
  return(list(Freq = dt_train_Freq, Loss = dt_train_Loss))
}



IBNR_Test <- function(dt_policy_claim, date_i, delta, k, reserving_dates, model_vars, verbose = FALSE) {
  
  # Create a combined TEST dataset across all k and j combos
  for (k in 1:k){
    if (k==1) dt_test <- NULL
    for (j in 1:(delta - k + 1)){
      dt_test <- rbind(dt_test, IBNR_Test_ijk(dt_policy_claim, date_i, j, k,reserving_dates, model_vars, verbose))
    }
  }
  return(dt_test)
}
