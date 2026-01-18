import { AgentAdapter } from './index.js';
import { execa } from 'execa';

export class CopilotAdapter implements AgentAdapter {
  name = 'Copilot CLI';

  async execute(context: string, command: string): Promise<boolean> {
    console.log('✈️ Copilot is flying...');
    
    try {
        // gh copilot suggest "..."
        console.log(`> Simulating Copilot execution for: "${command}"`);
        await new Promise(r => setTimeout(r, 1500));
        return true;
    } catch (e) {
        return false;
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
        await execa('gh', ['copilot', '--version']);
        return true;
    } catch {
        return false;
    }
  }
}
