*** What you need to do before running this code ***

sudo apt update
sudo install -y chromedriver (If it did not work then run the below command)


sudo apt install -y wget unzip
wget -N https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.183/linux64/chromedriver-linux64.zip
unzip -o chromedriver-linux64.zip
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm -rf chromedriver-linux64.zip chromedriver-linux64
chromedriver --version

** How to run the application **
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py