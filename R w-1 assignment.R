#R assignment w-1

## Assignment Week 1
https://github.com/absolutoslo/practice_assignment/blob/master/practice_assignment.rmd
## Unzip Specdata in R working directory
## check files
list.files("specdata")
[1] "001.csv" "002.csv" "003.csv" "004.csv" "005.csv" "006.csv" "007.csv" "008.csv"
  [9] "009.csv" "010.csv" "011.csv" "012.csv" "013.csv" "014.csv" "015.csv" "016.csv"
 [17] "017.csv" "018.csv" "019.csv" "020.csv" "021.csv" "022.csv" "023.csv" "024.csv"
 ## inspect one file
 read.csv("specdata/001.csv")
 1458 2006-12-28      NA      NA  1
1459 2006-12-29      NA      NA  1
1460 2006-12-30      NA      NA  1
1461 2006-12-31      NA      NA  1
## assing name to file
first=read.csv("specdata/001.csv")
## look for columns name
names(first)
## check length of the table (nrow)
length(first$Date)
[1] 1461
## check dim (nrow,ncol)
dim(first)
[1] 1461    4
summary(first)
         Date         sulfate          nitrate             ID   
 2003-01-01:   1   Min.   : 0.613   Min.   :0.1180   Min.   :1  
 2003-01-02:   1   1st Qu.: 2.210   1st Qu.:0.2835   1st Qu.:1  
 2003-01-03:   1   Median : 2.870   Median :0.4530   Median :1  
 2003-01-04:   1   Mean   : 3.881   Mean   :0.5499   Mean   :1  
 2003-01-05:   1   3rd Qu.: 4.730   3rd Qu.:0.6635   3rd Qu.:1  
 2003-01-06:   1   Max.   :19.100   Max.   :1.8300   Max.   :1  
 (Other)   :1455   NA's   :1344     NA's   :1339 
 str(first)
'data.frame':	1461 obs. of  4 variables:
 $ Date   : Factor w/ 1461 levels "2003-01-01","2003-01-02",..: 1 2 3 4 5 6 7 8 9 10 ...
 $ sulfate: num  NA NA NA NA NA NA NA NA NA NA ...
 $ nitrate: num  NA NA NA NA NA NA NA NA NA NA ...
 $ ID     : int  1 1 1 1 1 1 1 1 1 1 ...
 ## check first value of a column in data.frame(first)
 first[1, "Date"]
[1] 2003-01-01
1461 Levels: 2003-01-01 2003-01-02 2003-01-03 2003-01-04 2003-01-05 ... 2006-12-31
## check final date
first[1461, "Date"]
[1] 2006-12-31
1461 Levels: 2003-01-01 2003-01-02 2003-01-03 2003-01-04 2003-01-05 ... 2006-12-31
## create a subset of data
first[which(first$Date == 2006-12-31), "sulfate"]
## or
first[which(first[, "Date"] == 2006-12-31), "sulfate"]
numeric(0)
## or
subset() function
subset(...)

## back to all files - assign vector to list of files
> files = list.files("specdata")
> files
  [1] "001.csv" "002.csv" "003.csv" "004.csv" "005.csv" "006.csv" "007.csv" "008.csv"
  [9] "009.csv" "010.csv" "011.csv" "012.csv" "013.csv" "014.csv" "015.csv" "016.csv"
 [17] "017.csv" "018.csv" "019.csv" "020.csv" "021.csv" "022.csv" "023.csv" "024.csv"
 > files[1]
[1] "001.csv"
> files[1:5]
[1] "001.csv" "002.csv" "003.csv" "004.csv" "005.csv"
