import { AgentService, AgentRequestOptions } from '../spongecake-ui/frontend/services/AgentService';

async function main() {
  const options: AgentRequestOptions = {
    messages: 'Hello, agent!',
    safetyAcknowledged: true,
    autoMode: false,
  };

  try {
    const response = await AgentService.runAgent(options);
    console.log('Agent Response:', response);
  } catch (error) {
    console.error('Error running agent:', error);
  }
}

main();
