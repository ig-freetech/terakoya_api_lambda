if git diff --name-only HEAD^ HEAD -- functions/requirements.txt | grep "requirements.txt"; then
    echo 'requirements.txt has changed'
else 
    echo 'requirements.txt has not changed'
fi