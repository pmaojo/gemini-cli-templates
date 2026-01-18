import { spawn } from 'child_process';
import path from 'path';
import chalk from 'chalk';
import fs from 'fs/promises';

export class LoopMonitor {
  async start(): Promise<void> {
    console.log(chalk.bold.magenta('🚀 Launching the Real Ralph Loop...'));
    
    const skillDir = path.resolve(process.cwd(), '../.gemini/skills/ralph-wiggum/scripts');
    const ralphScript = path.join(skillDir, 'ralph.sh');
    const prdFile = path.join(skillDir, 'prd.json');

    // 1. Write the Mission (prd.json)
    // In a real app, this data comes from the PDR.md we just generated.
    const mission = {
      feature: "Ralph Manager Demo",
      branchName: "ralph/demo-loop",
      userStories: [
        {
          id: "1",
          title: "Verify project structure exists",
          passes: false
        },
        {
          id: "2",
          title: "Check if node_modules are installed",
          passes: false
        }
      ]
    };

    console.log(chalk.blue(`\n📝 Writing Mission to: ${prdFile}`));
    await fs.writeFile(prdFile, JSON.stringify(mission, null, 2));

    // 2. Execute Ralph
    console.log(chalk.dim(`Executing: ${ralphScript} 5`));
    
    // Pass '5' as max_iterations (the only arg ralph.sh accepts)
    const child = spawn(ralphScript, ['5'], {
        stdio: 'inherit',
        cwd: skillDir // Run inside the scripts dir so it finds prompt.md/prd.json
    });

    child.on('close', (code) => {
        if (code === 0) {
            console.log(chalk.green('\n✅ Ralph Loop completed all tasks!'));
        } else {
            console.log(chalk.red(`\n❌ Ralph Loop exited with code ${code}`));
        }
    });
  }
}
