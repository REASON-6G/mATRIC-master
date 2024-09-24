# /utils/conflict_resolution_layer.py

from datetime import timedelta, datetime
from app.database import DatabaseManager

class ConflictResolutionLayer:
    def __init__(self, cooldown_period: timedelta = timedelta(seconds=10)):
        # Define the cooldown period (default is 10 seconds)
        self.cooldown_period = cooldown_period

    def is_command_allowed(self, agent_id: str, db_manager: DatabaseManager) -> bool:
        """
        Check if a command for the agent is allowed (i.e., if the cooldown period has passed).
        Returns True if the command is allowed, False otherwise.
        """
        now = datetime.utcnow()
        print("now: ", now)

        # Step 1: Retrieve the last command from the DatabaseManager
        last_command = db_manager.get_last_command_for_agent(agent_id)
        print("last_command: ", last_command)

        # if last_command:
        #     last_command_time = last_command.last_command_time
        #     # If the last command was sent within the cooldown period, reject the new command
        #     if now - last_command_time < self.cooldown_period:
        #         return False
        # return True

    def register_command(self, agent_id: str, command: str, db_manager: DatabaseManager):
        """
        Register the current command for the agent by saving it in the database using DatabaseManager.
        """
        # Step 2: Save the command using the DatabaseManager
        db_manager.save_command_for_agent(agent_id, command)
