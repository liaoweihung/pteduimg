(() => {
    const form = document.getElementById('rx-form');
    const issueDate = document.getElementById('issue-date');
    const sameDay = document.getElementById('first-fill-same-day');
    const firstFillGroup = document.getElementById('first-fill-group');
    const firstFillOptions = document.getElementById('first-fill-options');
    const firstFillDate = document.getElementById('first-fill-date');
    const secondFillGroup = document.getElementById('second-fill-group');
    const secondFillDate = document.getElementById('second-fill-date');
    const refillCount = document.getElementById('refill-count');
    const refillTime = document.getElementById('refill-time');
    const thirdRefillButton = document.getElementById('third-refill-button');
    const supplyDays = document.getElementById('supply-days');
    const resultCard = document.getElementById('result-card');
    const message = document.getElementById('form-message');
    const warningBox = document.getElementById('warning-box');
    const nextWindowCard = document.getElementById('next-window-card');
    const todayFillButton = document.getElementById('today-fill');
    const todayResultCard = document.getElementById('today-result-card');

    const formatInput = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };
    const formatTaiwan = (date) => {
        const weekday = date.getDay() === 0 ? 7 : date.getDay();
        return `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')} (W${weekday})`;
    };
    const formatMonthDayWeek = (date) => {
        const weekday = date.getDay() === 0 ? 7 : date.getDay();
        return `${date.getMonth() + 1}/${date.getDate()} (W${weekday})`;
    };
    const addDays = (date, days) => {
        const result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    };
    const parseDate = (value) => value ? new Date(`${value}T00:00:00`) : null;

    function updateChoiceButtons(target, value) {
        document.querySelectorAll(`.choice-button[data-target="${target}"]`).forEach((button) => {
            const selected = button.dataset.value === value;
            button.classList.toggle('is-selected', selected);
            button.setAttribute('aria-pressed', String(selected));
        });
    }

    function renderFirstFillOptions() {
        const issued = parseDate(issueDate.value);
        firstFillOptions.textContent = '';
        if (!issued) return;

        for (let offset = 0; offset <= 3; offset += 1) {
            const date = addDays(issued, offset);
            const button = document.createElement('button');
            const value = formatInput(date);
            button.type = 'button';
            button.className = 'choice-button';
            button.dataset.firstFill = value;
            button.textContent = offset === 0 ? `處方當天（${formatMonthDayWeek(date)}）` : `第 ${offset + 1} 天（${formatMonthDayWeek(date)}）`;
            button.setAttribute('aria-pressed', String(value === firstFillDate.value));
            if (value === firstFillDate.value) button.classList.add('is-selected');
            button.addEventListener('click', () => {
                firstFillDate.value = value;
                secondFillDate.value = '';
                renderFirstFillOptions();
                syncSecondFill();
                runLogic();
            });
            firstFillOptions.appendChild(button);
        }
    }

    function syncFirstFill() {
        const issued = parseDate(issueDate.value);
        firstFillGroup.hidden = sameDay.checked;
        if (!issued) return;
        if (sameDay.checked) {
            firstFillDate.value = issueDate.value;
        } else if (!firstFillDate.value || firstFillDate.value < issueDate.value || firstFillDate.value > formatInput(addDays(issued, 3))) {
            firstFillDate.value = issueDate.value;
        }
        renderFirstFillOptions();
    }

    function syncSecondFill() {
        const first = parseDate(firstFillDate.value);
        const days = Number(supplyDays.value);
        const isThirdRefill = refillTime.value === '3';
        secondFillGroup.hidden = !isThirdRefill;
        if (!isThirdRefill || !first || !days) return;

        const earliestSecondFill = addDays(first, days - 10);
        secondFillDate.min = formatInput(earliestSecondFill);
        if (!secondFillDate.value) {
            secondFillDate.value = formatInput(earliestSecondFill);
        }
    }

    function syncRefillCount() {
        const hasThirdRefill = refillCount.value === '3';
        thirdRefillButton.hidden = !hasThirdRefill;
        if (!hasThirdRefill && refillTime.value === '3') {
            refillTime.value = '2';
            updateChoiceButtons('refill-time', '2');
        }
        syncSecondFill();
    }

    function setWarning(type, text) {
        warningBox.className = `warning-box ${type}`;
        warningBox.textContent = text;
    }

    function getRemainingDays(targetDate, previousFillDate, supplyDays) {
        if (!targetDate || !previousFillDate) return 0;
        const elapsedDays = Math.floor((targetDate - previousFillDate) / 86400000);
        return Math.max(0, supplyDays - elapsedDays);
    }

    function getToday() {
        const now = new Date();
        return new Date(now.getFullYear(), now.getMonth(), now.getDate());
    }

    function runTodayFill() {
        const issued = parseDate(issueDate.value);
        const days = Number(supplyDays.value);
        const count = Number(refillCount.value);
        const refill = Number(refillTime.value);
        if (!issued || !days || !count || !refill) {
            message.textContent = '請先填寫完整資料。';
            todayResultCard.hidden = true;
            return;
        }

        const today = getToday();
        const expiry = addDays(issued, Math.min(days * count, 90));
        const visit = addDays(expiry, days === 30 ? 1 : 0);
        const hasNextRefill = refill < count;
        const nextDate = addDays(today, days - 10);
        const nextDateGroup = document.getElementById('today-next-date-group');
        const todayWarning = document.getElementById('today-warning');

        document.getElementById('today-fill-date').textContent = formatTaiwan(today);
        document.getElementById('today-visit-date').textContent = formatTaiwan(visit);
        document.getElementById('today-expiry-date').textContent = formatTaiwan(expiry);
        nextDateGroup.hidden = !hasNextRefill || nextDate > expiry;
        if (!nextDateGroup.hidden) document.getElementById('today-next-date').textContent = formatTaiwan(nextDate);

        if (today > expiry) {
            todayWarning.className = 'warning-box danger';
            todayWarning.textContent = '今天已超過處方失效日，無法依本張處方領藥。';
        } else if (!hasNextRefill) {
            todayWarning.className = 'warning-box info';
            todayWarning.textContent = '本次為最後一次領藥，沒有後續可領藥日期。';
        } else if (nextDate > expiry) {
            todayWarning.className = 'warning-box danger';
            todayWarning.textContent = '下一次最早可領藥日已超過處方失效日。';
        } else {
            todayWarning.className = 'warning-box info';
            todayWarning.textContent = '下次領藥日依病人餘藥數小於或等於 10 天計算。';
        }
        message.textContent = '';
        todayResultCard.hidden = false;
        todayResultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function runLogic() {
        const issued = parseDate(issueDate.value);
        const first = parseDate(firstFillDate.value);
        const second = parseDate(secondFillDate.value);
        const days = Number(supplyDays.value);
        const count = Number(refillCount.value);
        const refill = Number(refillTime.value);
        if (!issued || !first || !days || (refill === 3 && !second)) {
            resultCard.hidden = true;
            message.textContent = '請先填寫完整資料。';
            return;
        }

        if (refill === 3 && second < addDays(first, days - 10)) {
            resultCard.hidden = true;
            message.textContent = '第二次領藥日期過早；為符合餘藥不大於 10 天，請選擇系統允許的日期或之後。';
            return;
        }

        const expiry = addDays(issued, Math.min(days * count, 90));
        const earliest = refill === 1
            ? new Date(first)
            : refill === 2
                ? addDays(first, days - 10)
                : addDays(second, days - 10);
        const latest = addDays(expiry, -(count - refill) * (days - 10));
        const visit = addDays(expiry, days === 30 ? 1 : 0);
        const thirdEligible = addDays(earliest, days - 10);
        const previousFill = refill === 1 ? null : refill === 2 ? first : second;
        const earliestRemaining = getRemainingDays(earliest, previousFill, days);
        const latestRemaining = getRemainingDays(latest, previousFill, days);
        const thirdEligibleRemaining = getRemainingDays(thirdEligible, earliest, days);
        const expiryRemaining = getRemainingDays(expiry, previousFill, days);
        const visitRemaining = getRemainingDays(visit, previousFill, days);
        document.getElementById('valid-window-start').textContent = formatTaiwan(earliest);
        document.getElementById('remaining-days').textContent = String(earliestRemaining);
        document.getElementById('valid-window-end').textContent = formatTaiwan(latest);
        document.getElementById('latest-remaining-days').textContent = String(latestRemaining);
        document.getElementById('latest-date-result').hidden = refill === 3;
        document.getElementById('third-eligible-date-result').hidden = count !== 3 || refill !== 2;
        document.getElementById('third-eligible-date').textContent = formatTaiwan(thirdEligible);
        document.getElementById('third-eligible-remaining-days').textContent = String(thirdEligibleRemaining);
        document.getElementById('expire-date').textContent = formatTaiwan(expiry);
        document.getElementById('expiry-remaining-days').textContent = String(expiryRemaining);
        document.getElementById('visit-date-result').hidden = false;
        document.getElementById('visit-date-output').textContent = formatTaiwan(visit);
        document.getElementById('visit-remaining-days').textContent = String(visitRemaining);
        nextWindowCard.hidden = true;
        message.textContent = '';
        if (earliest > expiry) {
            setWarning('danger', '依目前設定，最早可領日期已超過處方有效期限，請確認資料。');
        } else {
            setWarning('info', '各次領藥均以病人餘藥數小於或等於 10 天為原則計算。');
        }
        resultCard.hidden = false;
    }

    function setChoice(target, value) {
        document.getElementById(target).value = value;
        updateChoiceButtons(target, value);
        if (target === 'refill-count') syncRefillCount();
        if (target === 'refill-time' || target === 'supply-days') syncSecondFill();
        runLogic();
    }

    function resetCalculator() {
        issueDate.value = formatInput(addDays(new Date(), -14));
        sameDay.checked = true;
        refillCount.value = '3';
        refillTime.value = '2';
        supplyDays.value = '28';
        secondFillDate.value = '';
        updateChoiceButtons('refill-count', '3');
        updateChoiceButtons('refill-time', '2');
        updateChoiceButtons('supply-days', '28');
        syncFirstFill();
        syncRefillCount();
        syncSecondFill();
        resultCard.hidden = true;
        todayResultCard.hidden = true;
        message.textContent = '';
    }

    form.addEventListener('submit', (event) => { event.preventDefault(); runLogic(); });
    issueDate.addEventListener('change', () => { firstFillDate.value = ''; secondFillDate.value = ''; syncFirstFill(); syncSecondFill(); runLogic(); });
    sameDay.addEventListener('change', () => { syncFirstFill(); secondFillDate.value = ''; syncSecondFill(); runLogic(); });
    secondFillDate.addEventListener('change', runLogic);
    todayFillButton.addEventListener('click', runTodayFill);
    document.querySelectorAll('.choice-button[data-target]').forEach((button) => {
        button.addEventListener('click', () => setChoice(button.dataset.target, button.dataset.value));
    });
    window.setChoice = setChoice;
    window.runLogic = runLogic;
    window.resetCalculator = resetCalculator;
    resetCalculator();
})();
