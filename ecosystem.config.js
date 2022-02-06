module.exports = {
    apps: [{
        name: "emily",
        script: "poetry run python bot.py",
	    exp_backoff_restart_delay: 100
    }]

}
