export interface AgentAdapter {
  name: string;
  
  /**
   * Spawns the agent to work on a specific task context.
   * @param context The PRD/Task context
   * @param command The verification command
   */
  execute(context: string, command: string): Promise<boolean>;
  
  /**
   * Checks if the underlying tool is available
   */
  healthCheck(): Promise<boolean>;
}

export const AgentRegistry: Record<string, AgentAdapter> = {};

export function registerAdapter(adapter: AgentAdapter) {
  AgentRegistry[adapter.name] = adapter;
}
