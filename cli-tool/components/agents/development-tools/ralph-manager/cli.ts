#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import inquirer from 'inquirer';
import { Architect } from './core/architect.js';
import { LoopMonitor } from './core/loop-monitor.js';

const program = new Command();

program
  .name('ralph-manager')
  .description('The Meta-Manager for Agentic Software Development')
  .version('0.1.0');

program
  .command('new')
  .description('Start a new project from an Idea')
  .action(async () => {
    console.log(chalk.bold.green('🤖 Ralph Manager: Inception Mode'));
    
    // 1. Interview Phase
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'idea',
        message: 'What is your idea? (Briefly describe)',
      },
      {
        type: 'list',
        name: 'agent',
        message: 'Which agent workforce should we employ?',
        choices: ['Gemini (Native)', 'Claude (Anthropic)', 'Copilot CLI', 'Jules'],
      }
    ]);

    // 2. Architect Phase
    const architect = new Architect();
    console.log(chalk.blue(`\n🧠 Architecting solution for: "${answers.idea}"...`));
    await architect.draftSpecs(answers.idea);
    
    console.log(chalk.green('\n✅ Specs created! (See PDR.md)'));
    console.log(chalk.dim('Run "ralph-manager start" to begin execution.'));
  });

program
  .command('start')
  .description('Start the execution loop based on PDR')
  .action(async () => {
    console.log(chalk.bold.magenta('🔥 Igniting the Ralph Loop...'));
    const monitor = new LoopMonitor();
    await monitor.start();
  });

program.parse();
