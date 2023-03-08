#!/bin/bash
echo -e "\033[32mStart deployment. Please wait for deployment completed message.\033[m"
set -e
git pull git@github.com:Migheli/star-burger.git
. venv/bin/activate
pip install -r requirements.txt
npm ci
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
python manage.py collectstatic --noinput
python manage.py migrate
deactivate
systemctl daemon-reload


rollbar_name=$(hostname)
environment_name=undefined

while IFS== read -r variable value
do
  if [[ "$variable" == *"ROLLBAR_NAME"* ]]; then
    rollbar_name=$value
  elif [[ "$variable" == *"ROLLBAR_ACCESS_TOKEN"* ]]; then
    access_token=$value
  elif [[ "$variable" == *"ROLLBAR_ENVIRONMENT"* ]]; then
    environment_name=$value
  fi
done < .env


echo -e "\033[32mCongratulations! Project deployment is completed succesfully.\033[m"

username=$(whoami)
commit_hash=$(git rev-parse --short HEAD)


generate_post_data()
{
  cat <<EOF
{
  "environment": "$environment_name",
  "revision": "$commit_hash",
  "rollbar_name": "$rollbar_name",
  "local_username": "$username",
  "comment": "Autodeploy via bash scrypt",
  "status": "succeeded"
}
EOF
}

curl -H "X-Rollbar-Access-Token: $access_token" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d "$(generate_post_data)"

echo -e "\n From above you can see the status of your Rollbar notification about deployment"
