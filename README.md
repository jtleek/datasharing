How to share data with a statistician
===========

This is a guide for anyone who needs to share data with a statistician. The target audiences I have in mind are:

* Scientific collaborators who need statisticians to analyze data for them
* Students or postdocs in scientific disciplines looking for consulting advice
* Junior statistics students whose job it is to collate/clean data sets

The goals of this guide are to provide some instruction on the best way to share data to avoid the most common pitfalls
and sources of delay in the transition from data collection to data analysis. The Leek group works with a large
number of collaborators and the number one source of variation in the speed to results is the status of the data
when they arrive at the Leek group. Based on my conversations with other statisticians this is true nearly universally.

My strong feeling is that statisticians should be able to handle the data in whatever state they arrive. It is important
to see the raw data, understand the steps in the processing pipeline, and be able to incorporate hidden sources of
variability in one's data analysis. On the other hand, for many data types, the processing steps are well documented
and standardized. So the work of converting the data from raw form to directly analyzable form can be performed 
before calling on a statistician. This can dramatically speed the turnaround time, since the statistician doesn't
have to work through all the pre-processing steps first. 


What you should deliver to the statistician
====================

For maximum speed in the analysis this is the information you should pass to a statistician:

1. The raw data.
2. A [tidy data set](http://vita.had.co.nz/papers/tidy-data.pdf) 
3. A code book describing each variable and its values in the tidy data set.  
4. An explicit and exact recipe you used to go from 1 -> 2,3 

Let's look at each part of the data package you will transfer. 


### The raw data

It is critical that you include the rawest form of the data that you have access to. Here are some examples of the
raw form of data:

* The strange binary file your measurement machine spits out
* The unformated Excel file with 10 workbooks the company you contracted with sent you
* The complicated JSON data you got from scraping the Twitter API
* The hand-entered numbers you collected looking through a microscope

You know the raw data is in the right format if you: 

1. Ran no software on the data
2. Did not manipulate any of the numbers in the data
3. You did not remove any data from the data set
4. You did not summarize the data in any way

If you did any manipulation of the data at all it is not the raw form of the data. Reporting manipulated data
as raw data is a very common way to slow down the analysis process, since the analyst will often have to do a
forensic study of your data to figure out why the raw data looks weird. 

### The tidy data set

The general principles of tidy data are laid out by Hadley Wickham in [this paper](http://vita.had.co.nz/papers/tidy-data.pdf)
and [this video](http://vimeo.com/33727555). The paper and the video are both focused on the R package, which you
may or may not know how to use. Regardless the three general principles you should pay attention to are:

1. Each variable you measure should be in one column
2. Each different observation of that variable should be in a different row
3. There should be one table for each "kind" of variable
4. If you have multiple tables, they should include a row in the table that allows them to be linked


### The code book


### The instruction list/script





What you should expect from a statistician
====================




