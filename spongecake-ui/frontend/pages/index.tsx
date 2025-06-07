import { useState } from 'react';
import { AgentService, AgentRequestOptions } from '../services/AgentService';

const HomePage = () => {
  const [messages, setMessages] = useState('');
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunAgent = async () => {
    const options: AgentRequestOptions = {
      messages,
      safetyAcknowledged: true,
      autoMode: false,
    };

    try {
      const result = await AgentService.runAgent(options);
      setResponse(result);
      setError(null);
    } catch (err) {
      setError(err.message);
      setResponse(null);
    }
  };

  return (
    <div>
      <h1>Run Agent</h1>
      <textarea
        value={messages}
        onChange={(e) => setMessages(e.target.value)}
        placeholder="Enter messages for the agent"
      />
      <button onClick={handleRunAgent}>Run Agent</button>
      {response && (
        <div>
          <h2>Response:</h2>
          <pre>{JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
      {error && (
        <div>
          <h2>Error:</h2>
          <pre>{error}</pre>
        </div>
      )}
    </div>
  );
};

export default HomePage;
