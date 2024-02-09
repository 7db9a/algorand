# Use the official Algorand image
FROM algorand/algod:latest

# Set working directory
WORKDIR /algod

# Expose necessary ports
EXPOSE 8080 7833

# Default command to run the node
CMD ["algod", "-d", "/algod/data"]
