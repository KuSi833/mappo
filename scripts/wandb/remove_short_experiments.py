import os
import pyrootutils
import wandb

root = pyrootutils.setup_root(__file__, pythonpath=True, dotenv=True)

# Replace these with your actual project and group names
ENTITY = "kusi833"
PROJECT_NAME = "smac_v2_runs"
WANDB_API_KEY = os.getenv("WANDB_API_KEY")

wandb.login(key=WANDB_API_KEY)


def get_run_overview_url(run):
    return f"https://wandb.ai/{ENTITY}/{PROJECT_NAME}/runs/{run.id}/overview?workspace=user-{ENTITY}"


def prompt_for_deletion(run, reason):
    print(f"Run ID: {run.id} - Name: {run.name} - {reason}")
    print(f"   {get_run_overview_url(run)}")
    print("Would you like to delete? y/n")
    action = input()
    if action == "y":
        run.delete()
        print("DELETED")
    else:
        print("SKIPPED")


def delete_short_runs(entity, project, max_duration_minutes=5):
    api = wandb.Api()
    runs = api.runs(f"{entity}/{project}")

    short_runs = []
    for run in runs:
        if "_runtime" not in run.summary:
            short_runs.append(run)
            prompt_for_deletion(run, "NO RUNTIME")
        else:
            duration = run.summary["_runtime"]
            if duration < max_duration_minutes * 60:
                prompt_for_deletion(run,
                                    f"SHORT DURATION: {(duration / 60):.2f}m")


delete_short_runs(ENTITY, PROJECT_NAME)
