    function updateVisibilityAndCheckState() {
        const fields = [
            { checkbox: 'editTriggersCheckbox', field: 'editTriggersField', input: 'editTriggers' },
            { checkbox: 'editTriggerTimeCheckbox', field: 'editTriggerTimeField', input: 'editTriggerTime' },
            { checkbox: 'editTriggersAICheckbox', field: 'editTriggersAIField', input: 'editTriggersAI' },
            { checkbox: 'editTriggerAITimeCheckbox', field: 'editTriggerAITimeField', input: 'editTriggerAITime' },
            { checkbox: 'editBotReminderCheckbox', field: 'editBotReminderFields', input: 'editBotText', additionalInput: 'editBotInterval' },
            { checkbox: 'editManagerIntervalCheckbox', field: 'editManagerIntervalField', input: 'editManagerInterval' },
            { checkbox: 'editCallResponseCheckbox', field: 'editCallResponseField', input: 'editCallResponseText' },
            { checkbox: 'editBotStopCheckbox', field: 'editBotStopField', input: 'editBotStopTime', additionalCheckbox: 'editNotifyManagerCheckbox' }
        ];

        fields.forEach(({ checkbox, field, input, additionalInput, additionalCheckbox }) => {
            const checkboxElement = document.getElementById(checkbox);
            const fieldElement = document.getElementById(field);
            const inputElement = document.getElementById(input);

            checkboxElement.checked = inputElement.value !== '';
            fieldElement.style.display = checkboxElement.checked ? 'block' : 'none';

            if (additionalInput) {
                const additionalInputElement = document.getElementById(additionalInput);
                if (additionalInputElement) {
                    checkboxElement.checked = checkboxElement.checked || additionalInputElement.value !== '';
                }
            }

            if (additionalCheckbox) {
                const additionalCheckboxElement = document.getElementById(additionalCheckbox);
                if (additionalCheckboxElement) {
                    additionalCheckboxElement.checked = inputElement.value !== '';
                }
            }
        });
    }

    document.getElementById('editTriggersCheckbox').addEventListener('change', function () {
        let triggersField = document.getElementById('editTriggersField');
        if (this.checked) {
            triggersField.style.display = 'block';
        } else {
            triggersField.style.display = 'none';
            document.getElementById('editTriggers').value = '';
            document.getElementById('editTriggerTimeCheckbox').checked = false;
            document.getElementById('editTriggerTimeField').style.display = 'none';
            document.getElementById('editTriggerTime').value = '';
        }
    });

    document.getElementById('editTriggerTimeCheckbox').addEventListener('change', function () {
        let triggerTimeField = document.getElementById('editTriggerTimeField');
        if (this.checked) {
            triggerTimeField.style.display = 'block';
        } else {
            triggerTimeField.style.display = 'none';
            document.getElementById('editTriggerTime').value = '';
        }
    });

    document.getElementById('editTriggersAICheckbox').addEventListener('change', function () {
        let triggersAIField = document.getElementById('editTriggersAIField');
        if (this.checked) {
            triggersAIField.style.display = 'block';
        } else {
            triggersAIField.style.display = 'none';
            document.getElementById('editTriggersAI').value = '';
            document.getElementById('editTriggerAITimeCheckbox').checked = false;
            document.getElementById('editTriggerAITimeField').style.display = 'none';
            document.getElementById('editTriggerAITime').value = '';
        }
    });

    document.getElementById('editTriggerAITimeCheckbox').addEventListener('change', function () {
        let triggerAITimeField = document.getElementById('editTriggerAITimeField');
        if (this.checked) {
            triggerAITimeField.style.display = 'block';
        } else {
            triggerAITimeField.style.display = 'none';
            document.getElementById('editTriggerAITime').value = '';
        }
    });

    document.getElementById('editBotReminderCheckbox').addEventListener('change', function () {
        let botReminderFields = document.getElementById('editBotReminderFields');
        if (this.checked) {
            botReminderFields.style.display = 'block';
        } else {
            botReminderFields.style.display = 'none';
            document.getElementById('editBotText').value = '';
            document.getElementById('editBotInterval').value = '';
        }
    });

    document.getElementById('editManagerIntervalCheckbox').addEventListener('change', function () {
        let managerIntervalField = document.getElementById('editManagerIntervalField');
        if (this.checked) {
            managerIntervalField.style.display = 'block';
        } else {
            managerIntervalField.style.display = 'none';
            document.getElementById('editManagerInterval').value = '';
        }
    });

    document.getElementById('editCallResponseCheckbox').addEventListener('change', function () {
        let callResponseField = document.getElementById('editCallResponseField');
        if (this.checked) {
            callResponseField.style.display = 'block';
        } else {
            callResponseField.style.display = 'none';
            document.getElementById('editCallResponseText').value = '';
        }
    });

    document.getElementById('editBotStopCheckbox').addEventListener('change', function () {
        let botStopField = document.getElementById('editBotStopField');
        if (this.checked) {
            botStopField.style.display = 'block';
        } else {
            botStopField.style.display = 'none';
            document.getElementById('editBotStopTime').value = '';
            document.getElementById('editNotifyManagerCheckbox').checked = false;
        }
    });

    // Вызов функции для обновления видимости полей при открытии модального окна
    $('#editAccountModal').on('show.bs.modal', function (e) {
        updateVisibilityAndCheckState();
    });