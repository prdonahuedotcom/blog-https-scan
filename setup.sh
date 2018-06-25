sudo apt-get -y update
sudo apt-get -y install dnsutils unzip git jq tcpdump 

# for building python
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev

export USER=$(curl -sf http://metadata/computeMetadata/v1/instance/attributes/username -H "Metadata-Flavor: Google")
echo "USER is $USER"
export HOME="/home/$USER"
echo "HOME is $HOME"
export GOVER="go1.10.3.linux-amd64.tar.gz"

curl -sS -o $GOVER "https://dl.google.com/go/$GOVER"
tar -C /usr/local -xzf $GOVER

cat <<'EOF' | tee -a $HOME/.bashrc
export GOPATH=$HOME/go
export PATH=$PATH:/usr/local/go/bin:$HOME/.pyenv/bin
alias l='ls -altr'
EOF

cat <<'EOF' | tee -a $HOME/.profile
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
EOF

mkdir $HOME/go
export GOPATH=$HOME/go 
export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin:$HOME/.pyenv/bin

# install zgrab
go get github.com/zmap/zgrab
go get github.com/zmap/zdns/zdns

# use cloudflare's 1.1.1.1 instead of the google assigned nameservers (to avoid lookup timeouts)
sed -ie 's/nameserver.*$/nameserver 1.1.1.1/' /etc/resolv.conf

echo <<'EOF' | tee $HOME/run.sh
#!/bin/bash

cd $HOME

# set up python environment for processing output
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
pyenv update
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# install python and set up virtualenv for scripts
pyenv install 3.6.5
pyenv virtualenv 3.6.5 scan
pyenv local scan

## download and unzip the alexa top 1 million
curl -sS -o top-1m.csv.zip https://s3.amazonaws.com/alexa-static/top-1m.csv.zip
unzip top-1m.csv.zip

# up the open file descriptor limit (just in case)
ulimit -n 65536

# do dns lookup on apex:
# - if we get a value, use it
# - if not, do dns lookup on www.$APEX and use that if available, otherwise skip
cat top-1m.csv | $GOPATH/bin/zdns ALOOKUP --alexa --retries 5 -output-file lookups.json
cat top-1m.csv | sed -e 's/,/,www./' | $GOPATH/bin/zdns ALOOKUP --alexa --retries 5 -output-file www-lookups.json

# stitch dns records together (these are all magic filenames for now; would be good to argparse them)
ls -al lookups.json www-lookups.json
python dns.py
ls hosts.csv

# scan everything over TCP 80
export USERAGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"
cat hosts.csv | $GOPATH/bin/zgrab -timeout 20 -http="/" -http-max-size 4 -http-max-redirects 7 -http-user-agent "$USERAGENT" -output-file all.json -log-file all.log

# process output (more magical file names)
python analyze.py >> results.txt 2>&1
ls -al http.csv
wc -l http.csv

# rescan the non-redirected HTTP hosts explicitly over HTTPS
cat http.csv | $GOPATH/bin/zgrab -timeout 20 -tls -port 443 -http="/" -http-max-size 128 -http-max-redirects 7 -http-user-agent "$USERAGENT" -output-file $HOME/http.json -log-file $HOME/http.log
python analyze-http.py >> results.txt 2>&1

echo "Done!"
cat results.txt
EOF

chmod +x $HOME/run.sh
chown -R $USER:$USER $HOME
echo "Login as $USER and execute run.sh in $HOME."