const { exec } = require("child_process");
const fs = require("fs-extra");
const path = require("path");

/**
 * ProcessDetector - Handles Gemini CLI process detection and conversation matching
 * Extracted from monolithic analytics.js for better maintainability
 */
class ProcessDetector {
  constructor() {
    // Cache for process detection to avoid repeated shell commands
    this.processCache = {
      data: null,
      timestamp: 0,
      ttl: 500, // 500ms cache
    };
  }

  /**
   * Detect running Gemini CLI processes
   * @returns {Promise<Array>} Array of active Gemini processes
   */
  async detectRunningGeminiProcesses() {
    // Check cache first
    const now = Date.now();
    if (
      this.processCache.data &&
      now - this.processCache.timestamp < this.processCache.ttl
    ) {
      return this.processCache.data;
    }

    return new Promise((resolve) => {
      // Search for processes containing 'gemini' but exclude our own analytics process and system processes
      exec(
        'ps aux | grep -i gemini | grep -v grep | grep -v analytics | grep -v "/Applications/Gemini.app" | grep -v "npm start" | grep -v chats-mobile',
        (error, stdout) => {
          if (error) {
            resolve([]);
            return;
          }

          console.log("🔍 Raw Gemini processes output:", stdout); // Debug output

          const processes = stdout
            .split("\n")
            .filter((line) => line.trim())
            .filter((line) => {
              // More flexible Gemini CLI process detection
              const fullCommand = line.split(/\s+/).slice(10).join(" ");
              const isGeminiProcess =
                fullCommand.includes("gemini") &&
                !fullCommand.includes("chrome_crashpad_handler") &&
                !fullCommand.includes("create-gemini-config") &&
                !fullCommand.includes("chats-mobile") &&
                !fullCommand.includes("analytics") &&
                // Allow various Gemini CLI invocations
                (fullCommand.trim() === "gemini" ||
                  fullCommand.includes("gemini --") ||
                  fullCommand.includes("gemini ") ||
                  fullCommand.includes("/gemini") ||
                  fullCommand.includes("bin/gemini"));

              if (isGeminiProcess) {
                console.log("✅ Found Gemini process:", fullCommand);
              }

              return isGeminiProcess;
            })
            .map((line) => {
              const parts = line.split(/\s+/);
              const fullCommand = parts.slice(10).join(" ");

              // Extract useful information from command
              const cwdMatch = fullCommand.match(/--cwd[=\s]+([^\s]+)/);
              let workingDir = cwdMatch ? cwdMatch[1] : "unknown";

              // Skip pwdx for now since it doesn't exist on macOS

              return {
                pid: parts[1],
                command: fullCommand,
                workingDir: workingDir,
                startTime: new Date(), // For now we use current time
                status: "running",
                user: parts[0],
              };
            });

          // Cache the result
          this.processCache = {
            data: processes,
            timestamp: now,
            ttl: 500,
          };

          resolve(processes);
        }
      );
    });
  }

  /**
   * Enrich conversation data with running process information
   * @param {Array} conversations - Array of conversation objects
   * @param {string} geminiDir - Path to Gemini directory for file operations
   * @param {Object} stateCalculator - StateCalculator instance for state calculations
   * @returns {Promise<Object>} Object with enriched conversations and orphan processes
   */
  async enrichWithRunningProcesses(conversations, geminiDir, stateCalculator) {
    try {
      const runningProcesses = await this.detectRunningGeminiProcesses();

      // Add active process information to each conversation
      for (const conversation of conversations) {
        // Look for active process for this project
        // If workingDir is unknown, match with the most recently modified conversation
        let matchingProcess = runningProcesses.find(
          (process) =>
            process.workingDir.includes(conversation.project) ||
            process.command.includes(conversation.project)
        );

        // Fallback: if no direct match and workingDir is unknown,
        // assume the most recently modified conversation belongs to the active process
        if (
          !matchingProcess &&
          runningProcesses.length > 0 &&
          runningProcesses[0].workingDir === "unknown"
        ) {
          // Find the most recently modified conversation
          const sortedConversations = [...conversations].sort(
            (a, b) => new Date(b.lastModified) - new Date(a.lastModified)
          );

          if (conversation === sortedConversations[0]) {
            matchingProcess = runningProcesses[0];
          }
        }

        if (matchingProcess) {
          // ENRICH without changing existing logic
          conversation.runningProcess = {
            pid: matchingProcess.pid,
            startTime: matchingProcess.startTime,
            workingDir: matchingProcess.workingDir,
            hasActiveCommand: true,
          };

          // Only change status if not already marked as active by existing logic
          if (conversation.status !== "active") {
            conversation.status = "active";
            conversation.statusReason = "running_process";
          }

          // Recalculate conversation state with process information
          const conversationFile = path.join(geminiDir, conversation.fileName);
          try {
            const content = await fs.readFile(conversationFile, "utf8");
            const parsedMessages = content
              .split("\n")
              .filter((line) => line.trim())
              .map((line) => JSON.parse(line));

            const stats = await fs.stat(conversationFile);
            conversation.conversationState =
              stateCalculator.determineConversationState(
                parsedMessages,
                stats.mtime,
                conversation.runningProcess
              );
          } catch (error) {
            // If we can't read the file, keep the existing state
          }
        } else {
          conversation.runningProcess = null;
        }
      }

      // Disable orphan process detection to reduce noise
      const orphanProcesses = [];

      return {
        conversations,
        orphanProcesses,
        activeProcessCount: runningProcesses.length,
      };
    } catch (error) {
      // Silently handle process detection errors
      return {
        conversations,
        orphanProcesses: [],
        activeProcessCount: 0,
      };
    }
  }

  /**
   * Get cached processes without triggering detection
   * @returns {Array} Cached process data or empty array
   */
  getCachedProcesses() {
    const now = Date.now();
    if (
      this.processCache.data &&
      now - this.processCache.timestamp < this.processCache.ttl
    ) {
      return this.processCache.data;
    }
    return [];
  }

  /**
   * Clear process cache to force fresh detection
   */
  clearCache() {
    this.processCache = {
      data: null,
      timestamp: 0,
      ttl: 500,
    };
  }

  /**
   * Check if there are any active Gemini processes
   * @returns {Promise<boolean>} True if there are active processes
   */
  async hasActiveProcesses() {
    const processes = await this.detectRunningGeminiProcesses();
    return processes.length > 0;
  }

  /**
   * Get process statistics
   * @returns {Promise<Object>} Process statistics
   */
  async getProcessStats() {
    const processes = await this.detectRunningGeminiProcesses();
    return {
      total: processes.length,
      withKnownWorkingDir: processes.filter((p) => p.workingDir !== "unknown")
        .length,
      withUnknownWorkingDir: processes.filter((p) => p.workingDir === "unknown")
        .length,
      processes: processes,
    };
  }

  /**
   * Match a specific process to conversations
   * @param {Object} process - Process object
   * @param {Array} conversations - Array of conversation objects
   * @returns {Object|null} Matched conversation or null
   */
  matchProcessToConversation(process, conversations) {
    // Direct match by working directory or project name
    let match = conversations.find(
      (conv) =>
        process.workingDir.includes(conv.project) ||
        process.command.includes(conv.project)
    );

    // Fallback for unknown working directories
    if (
      !match &&
      process.workingDir === "unknown" &&
      conversations.length > 0
    ) {
      // Match to most recently modified conversation
      const sorted = [...conversations].sort(
        (a, b) => new Date(b.lastModified) - new Date(a.lastModified)
      );
      match = sorted[0];
    }

    return match;
  }
}

module.exports = ProcessDetector;
