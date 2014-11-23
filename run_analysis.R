##
##  1. Merges the training and the test sets to create one data set.
##
install.packages("dplyr")
library(dplyr)
install.packages("data.table")
library(data.table)
library(reshape)


## Bring in the data labels from the activity_labels.txt and create a data frame
activity_labels <- read.table("activity_labels.txt")

## Bring in the data labels from the features.txt and create a data frame
features_labels <- read.table("features.txt")

## Bring in the data labels in subject_t.txt
subject_test_labels <- read.table("test/subject_test.txt", col.names="Subject")
subject_train_labels <- read.table("train/subject_train.txt", col.names="Subject")

## Bring in the data for y_t.txt files
y_test <- read.table("test/y_test.txt", col.names="Activity")
y_train <- read.table("train/y_train.txt", col.names="Activity")


##
##  3. Uses descriptive activity names to name the activities in the data set
##
y_test$Activity <- paste(y_test[, 1], " - ", activity_labels[y_test[,1], 2])
y_train$Activity <- paste(y_train[, 1], " - ", activity_labels[y_train[, 1], 2])

## Create vectors to hold column names for Train and Test data frames upon ingestion
##
##  4. Appropriately labels the data set with descriptive variable names
##
column.Names = as.vector(features_labels$V2)
column.Names = make.names(column.Names)

## Create Train data frame 
Training <- read.table("./train/X_train.txt",
                      col.names=column.Names,
                      stringsAsFactors=FALSE)
Training <- cbind(Training, subject_train_labels)
Training <- cbind(Training, y_train)


## Create Test data frame and cbind the Training label
Testing <- read.table("./test/X_test.txt",
                       col.names=column.Names,
                       stringsAsFactors=FALSE)
Testing <- cbind(Testing, subject_test_labels)
Testing <- cbind(Testing, y_test)

## Rbind_list from dplyr is used to append Training and Testing data frames together
## Need install.packages("dplyr") and library(dplyr)
TestTrain <- rbind_list(Training, Testing)

##
##  2. Extracts only the measurements on the mean and standard deviation for each measurement. 
##
subject = TestTrain[c("Subject", "Activity")]
MeanVariables <- select(TestTrain, contains("mean"))
STDVariables <- select(TestTrain, contains("std"))
StatTrain <- cbind(MeanVariables, STDVariables)

##
##  Add columns for Subject and Activity 
##
StatTrain <- cbind(StatTrain, subject)


##
##  5. From the data set in step 4, creates a second, independent tidy data set with 
##       the average of each variable for each activity and each subject.
##
keyVars <- c("Activity", "Subject")

Stat_DT <- data.table(StatTrain)
Stat_DT <- setkeyv(Stat_DT, keyVars)
meltTrain <- melt(Stat_DT, id.vars = keyVars)
Train <- cast(Activity + variable ~ Subject, data =  meltTrain, fun=mean)
write.table(Train, "Reilly D GettingData classProject.txt", row.names=FALSE)