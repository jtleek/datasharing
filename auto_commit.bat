@echo off
cd /d C:\Users\ACER-NITRO\Desktop\github\datasharing

:: Generate a random number of commits (between 2 and 5)
set /a commits=%random% %% 4 + 2

:: Debugging message
echo "Starting Auto Commit Script..."
echo "Total Commits: %commits%"
echo. 

:: Loop through commits with individual push per commit
for /L %%i in (1,1,%commits%) do (
    echo "Committing: %%i / %commits% at %time%"
    
    echo Log entry %date% %time% >> log.txt
    git add log.txt

    git commit -m "Auto-update: %date% %time%" || (
        echo "Commit failed!"
        exit /b
    )

    :: Push after every commit
    git push origin main || (
        echo "Push failed!"
        exit /b
    )

    timeout /t 5 >nul
)

echo "Finished all commits."
exit
