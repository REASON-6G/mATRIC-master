import type { WebSocketService, WebSocketMessage } from "../client"

// Timestamp formatter
const getTimestamp = () => new Date().toISOString();

// Create colored console logging
const logger = {
  info: (message: string) => console.log(`\x1b[36m[${getTimestamp()}] INFO: ${message}\x1b[0m`),
  success: (message: string) => console.log(`\x1b[32m[${getTimestamp()}] SUCCESS: ${message}\x1b[0m`),
  warning: (message: string) => console.log(`\x1b[33m[${getTimestamp()}] WARNING: ${message}\x1b[0m`),
  error: (message: string) => console.log(`\x1b[31m[${getTimestamp()}] ERROR: ${message}\x1b[0m`),
  debug: (message: string) => console.log(`\x1b[90m[${getTimestamp()}] DEBUG: ${message}\x1b[0m`)
};

async function connectToWebSocket() {
  logger.info('Initializing WebSocket service...');
  let wsService: WebSocketService;

  // Track connection attempts
  let connectionAttempts = 0;
  const maxAttempts = 3;

  async function attemptConnection(): Promise<void> {
    const jobNumber = '1dd22d43-79c9-485d-9689-af49f2ce9ec8';
    connectionAttempts++;

    logger.info(`Attempting to connect (Attempt ${connectionAttempts}/${maxAttempts})...`);
    logger.debug(`Job Number: ${jobNumber}`);

    try {
      await wsService.connect(jobNumber);
      logger.success('Successfully connected to WebSocket server');

      // Set up message handling
      logger.info('Setting up message handlers...');
      wsService.onMessage((message: WebSocketMessage) => {
        logger.info('Received new message:');
        logger.debug(`Message Type: ${message.type}`);
        logger.debug(`Message Data: ${JSON.stringify(message.data, null, 2)}`);

        // Handle different message types
        switch(message.type) {
          case 'AGENT_DETAILS':
            logger.info('Received agent details');
            break;
          case 'STATUS_UPDATE':
            logger.info('Received status update');
            break;
          default:
            logger.warning(`Unhandled message type: ${message.type}`);
        }
      });

      // Send test messages
      logger.info('Sending test messages...');

      // Message 1: Get agent details
      logger.debug('Sending GET_AGENT_DETAILS message');
      wsService.sendMessage({
        type: 'GET_AGENT_DETAILS',
        data: { requestId: 'req-001' }
      });

      // Message 2: Update status
      logger.debug('Sending UPDATE_STATUS message');
      wsService.sendMessage({
        type: 'UPDATE_STATUS',
        data: {
          status: 'active',
          timestamp: new Date().toISOString()
        }
      });

      // Set up connection monitoring
      setInterval(() => {
        if (wsService.isConnected()) {
          logger.debug('Connection health check: OK');
        } else {
          logger.warning('Connection health check: Disconnected');
          attemptReconnection();
        }
      }, 5000);

    } catch (error) {
      logger.error(`Connection attempt ${connectionAttempts} failed: ${error}`);

      if (connectionAttempts < maxAttempts) {
        logger.info('Retrying connection in 5 seconds...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        return attemptConnection();
      } else {
        logger.error('Max connection attempts reached. Giving up.');
        throw error;
      }
    }
  }

  async function attemptReconnection() {
    logger.warning('Connection lost. Attempting to reconnect...');
    connectionAttempts = 0;
    try {
      await attemptConnection();
    } catch (error) {
      logger.error('Failed to reconnect after multiple attempts');
    }
  }

  // Start the connection process
  try {
    await attemptConnection();

    // Clean up function
    const cleanup = () => {
      logger.info('Cleaning up WebSocket connection...');
      wsService.disconnect();
      logger.success('WebSocket connection closed successfully');
      process.exit(0);
    };

    // Handle graceful shutdown
    process.on('SIGINT', cleanup);
    process.on('SIGTERM', cleanup);

  } catch (error) {
    logger.error(`Fatal error: ${error}`);
    process.exit(1);
  }
}

// Run the example
logger.info('Starting WebSocket example...');
connectToWebSocket().catch(error => {
  logger.error(`Unhandled error: ${error}`);
  process.exit(1);
});
