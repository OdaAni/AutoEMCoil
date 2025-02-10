# Start with Ubuntu 22.04 as our base Linux system
FROM ubuntu:22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install all the necessary software packages
RUN apt-get update && apt-get install -y \
    git \                    # For cloning repositories
    cmake \                  # For building software
    build-essential \        # Compilers and build tools
    libhdf5-dev \           # HDF5 library for data storage
    libvtk9-dev \           # Visualization toolkit
    libboost-all-dev \      # C++ boost libraries
    libcgal-dev \           # Computational geometry
    libtinyxml-dev \        # XML parsing
    python3-pip \           # Python package manager
    python3-numpy \         # Numerical computing
    python3-h5py           # HDF5 for Python

# Build and install CSXCAD (CAD tool for OpenEMS)
WORKDIR /opt
RUN git clone https://github.com/thliebig/CSXCAD.git && \
    cd CSXCAD && \
    mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install

# Build and install OpenEMS
RUN git clone https://github.com/thliebig/openEMS.git && \
    cd openEMS && \
    mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install

# Set up Python environment
ENV PYTHONPATH=/usr/local/lib/python3/dist-packages:$PYTHONPATH

# Set the working directory to /app (this is where your code will go)
WORKDIR /app
