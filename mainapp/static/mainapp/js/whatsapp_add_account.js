    document.getElementById('addTriggersCheckbox').addEventListener('change', function () {
        let triggersField = document.getElementById('addTriggersField');
        if (this.checked) {
            triggersField.style.display = 'block';
        } else {
            triggersField.style.display = 'none';
            document.getElementById('addTriggers').value = '';
            document.getElementById('addTriggerTimeCheckbox').checked = false;
            document.getElementById('addTriggerTimeField').style.display = 'none';
            document.getElementById('addTriggerTime').value = '';
        }
    });

    document.getElementById('addTriggerTimeCheckbox').addEventListener('change', function () {
        let triggerTimeField = document.getElementById('addTriggerTimeField');
        if (this.checked) {
            triggerTimeField.style.display = 'block';
        } else {
            triggerTimeField.style.display = 'none';
            document.getElementById('addTriggerTime').value = '';
        }
    });

    document.getElementById('addTriggersAICheckbox').addEventListener('change', function () {
        let triggersAIField = document.getElementById('addTriggersAIField');
        if (this.checked) {
            triggersAIField.style.display = 'block';
        } else {
            triggersAIField.style.display = 'none';
            document.getElementById('addTriggersAI').value = '';
            document.getElementById('addTriggerAITimeCheckbox').checked = false;
            document.getElementById('addTriggerAITimeField').style.display = 'none';
            document.getElementById('addTriggerAITime').value = '';
        }
    });

    document.getElementById('addTriggerAITimeCheckbox').addEventListener('change', function () {
        let triggerAITimeField = document.getElementById('addTriggerAITimeField');
        if (this.checked) {
            triggerAITimeField.style.display = 'block';
        } else {
            triggerAITimeField.style.display = 'none';
            document.getElementById('addTriggerAITime').value = '';
        }
    });

    document.getElementById('addBotReminderCheckbox').addEventListener('change', function () {
        let botReminderFields = document.getElementById('addBotReminderFields');
        if (this.checked) {
            botReminderFields.style.display = 'block';
        } else {
            botReminderFields.style.display = 'none';
            document.getElementById('addBotText').value = '';
            document.getElementById('addBotInterval').value = '';
        }
    });

    document.getElementById('addManagerIntervalCheckbox').addEventListener('change', function () {
        let managerIntervalField = document.getElementById('addManagerIntervalField');
        if (this.checked) {
            managerIntervalField.style.display = 'block';
        } else {
            managerIntervalField.style.display = 'none';
            document.getElementById('addManagerInterval').value = '';
        }
    });

    document.getElementById('addCallResponseCheckbox').addEventListener('change', function () {
        let callResponseField = document.getElementById('addCallResponseField');
        if (this.checked) {
            callResponseField.style.display = 'block';
        } else {
            callResponseField.style.display = 'none';
            document.getElementById('addCallResponseText').value = '';
        }
    });

    document.getElementById('addBotStopCheckbox').addEventListener('change', function () {
        let botStopField = document.getElementById('addBotStopField');
        if (this.checked) {
            botStopField.style.display = 'block';
        } else {
            botStopField.style.display = 'none';
            document.getElementById('addBotStopTime').value = '';
            document.getElementById('notifyManagerCheckbox').checked = false;
        }
    });