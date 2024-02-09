# Use the official Algorand image
FROM algorand/algod:latest

# Set working directory
WORKDIR /algod

# Copy the network template and initialization script
COPY my_network_template.json /algod/my_network_template.json
COPY initialize-network.sh /algod/initialize-network.sh

# Expose necessary ports
EXPOSE 8080 7833

# Run the network initialization script
CMD ["sh", "/algod/initialize-network.sh"]
