import argparse
import json
import os
import time
from datetime import datetime

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Name of the step/agent/script")
    parser.add_argument("--type", required=True, help="Workflow, Agent, Skill, Script")
    parser.add_argument("--path", required=True, help="Path or Identifier")
    parser.add_argument("--role", default="Task Executor", help="Role description")
    parser.add_argument("--model", default="N/A", help="Model used")
    parser.add_argument("--reasoning", default="-", help="Reason for model choice")
    parser.add_argument("--status", required=True, choices=["START", "END"], help="START or END")
    parser.add_argument("--log-file", default="analysis/execution_log.json", help="Path to log file")
    
    args = parser.parse_args()
    
    log_entry = {
        "name": args.name,
        "type": args.type,
        "path": args.path,
        "role": args.role,
        "model": args.model,
        "reasoning": args.reasoning,
        "status": args.status,
        "timestamp": datetime.now().isoformat(),
        "timestamp_unix": time.time()
    }
    
    # Ensure dir exists
    os.makedirs(os.path.dirname(args.log_file), exist_ok=True)
    
    # Read existing
    logs = []
    if os.path.exists(args.log_file):
        try:
            with open(args.log_file, "r") as f:
                logs = json.load(f)
        except:
            logs = []
            
    logs.append(log_entry)
    
    with open(args.log_file, "w") as f:
        json.dump(logs, f, indent=2)
        
    print(f"📋 Logged {args.status} for {args.name}")

if __name__ == "__main__":
    main()
