# Use the official Algorand image
FROM algorand/algod:latest

# Set working directory
WORKDIR /algod

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv

# Create a virtual environment and activate it
RUN python3 -m venv /algodenv
ENV PATH="/algodenv/bin:$PATH"

# Install Algorand Python SDK and PyTeal in the virtual environment
RUN pip3 install py-algorand-sdk pyteal

# Copy the network template, initialization script, and experiment scripts
COPY algorand/configs/my_network_template.json /algod/my_network_template.json
COPY algorand/initialize-network.sh /algod/initialize-network.sh
COPY algorand/lib/ /algod/lib/
COPY algorand/contracts/ /algod/contracts/
COPY algorand/tests/ /algod/tests/
COPY algorand/experiments/ /algod/experiments/
COPY algorand/examples/ /algod/examples/
COPY algorand/algorand-accounts/ /algod/algorand-accounts/
COPY algorand/scripts/name_to_address.py /algod/name_to_address.py

# Expose necessary ports
EXPOSE 8080 7833

# Run the network initialization script
CMD ["sh", "/algod/initialize-network.sh"]

