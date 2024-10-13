# Update gcc to gcc-12
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt install gcc-12 g++-12
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 100 --slave /usr/bin/g++ g++ /usr/bin/g++-12

# Install nghttp2
sudo apt-get install g++ clang make binutils autoconf automake \
  autotools-dev libtool pkg-config \
  zlib1g-dev libssl-dev libxml2-dev libev-dev \
  libevent-dev libjansson-dev \
  libc-ares-dev libjemalloc-dev libsystemd-dev \
  ruby-dev bison libelf-dev
git clone https://github.com/nghttp2/nghttp2.git
cd nghttp2
git submodule update --init
autoreconf -i
automake
autoconf
./configure --enable-app
make
# wget https://github.com/nghttp2/nghttp2/releases/download/v1.63.0/nghttp2-1.63.0.tar.bz2
# tar xf nghttp2-1.63.0.tar.bz2
# cd nghttp2-1.63.0
# ./configure --enable-app
# make