if git diff HEAD..origin/develop -- functions/requirements.txt | grep "requirements.txt"; then
    echo 'requirements.txt has changed'
else 
    echo 'requirements.txt has not changed'
fi