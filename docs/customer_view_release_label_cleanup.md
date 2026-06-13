# Customer-view release-label cleanup

This patch removes local prototype / local checkpoint wording from the dashboard
source and replaces it with beta-release wording suitable for a customer-facing
preview.

It patches:

`app\paid_simulator\config_form_app.py`

It does not change the simulator engine or option calculations.

Run the patch script first:

`app\run_customer_view_release_label_cleanup.py`

Then run the check:

`app\run_customer_view_release_label_cleanup_check.py`
