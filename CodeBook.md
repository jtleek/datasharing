---
title: "CodeBook"
author: "Donald J Reilly"
date: "Saturday, November 22, 2014"
output: html_document
---
This is the markdown file describing the sequence of events, starting with the raw data, that occurred to create the output file from my run.analysis.R file run against the Samsung HCI VAR data.

There are a number of datasets provided that will need to be brought together for our purposes into a single data table for analysis.  The data has been broken up into two datasets, train and test, with no accompanying data labels or metadata.  This information is provided in accompanying datasets and needs to be consolidated for our purposes. We begin by creating a set of data frames that ingest the label data.

1. Ingest Activity labels - WALKING, WALKING_UPSTAIRS, WALKING_DOWNSTAIRS, SITTING, STANDING, LAYING from                                                                    activity_labels.txt
2. Ingest Feature labels - this is a 561-label vector of variable names from features.txt which is a guide to the raw data measurements of the device and some preliminary analysis (mean, std)
3. Ingest subject labels from train and test subject files to indicate the subject the measurement was taken from, subject_train.txt and subject_test.txt
4. Ingest Activity labels from train and test y files that indicate the Activity being undertaken for each measurement, y_train.txt and y_test.txt
5. Activity data was originally stored as Integer data "1" for WALKING, etc. for our purposes the Integers were enhanced to associate text descriptions, but still keeping the integers for sorting purposes. So, a string was created so "1" became "1 - WALKING"
6. Feature labels (variable names) were associated with the target data file (ingested in step 2 above). Some text analysis was done on the variable names to ensure validity and consistency.
7. Create Train data frame - ingesting the training dataset, x_train.txt and enhancing it with Subject and Activity data
8. Create Test data frame - ingesting the testing dataset, x_test.txt and enhancing it with Subject and Activity data
9. Appending the two datasets, train and test, into a single data frame, TestTrain.
10. Extract into new dataframe, StatTrain, only those variables that represent mean and Standard Deviation statistical analysis, while maintaining the Subject and Activity data associated in steps 3 & 4 above.
11. Create a separate, tidy dataset representing the average of each variable for each activity and each subject.
12. Create a data table named Train that sorts the data by Activity and presents the mean of each 
associated variable for each subject. Write this dataset out as a .txt file named "Reilly d GettingData classProject.txt".


```{r}
names(Stat_DT)
```

