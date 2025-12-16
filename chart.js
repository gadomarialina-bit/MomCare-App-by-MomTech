/* Custom properties for easy color changes */
:root {
    --main-green: #0f4a1c;
    --light-green: #4c8f2a;
    --background-color: #cdebf3;
    --text-color: #333;
    --happy-color: #4CAF50;
    --neutral-color: #03A9F4;
    --tired-color: #E57373;
    --stressed-color: #000000;
}

body {
    margin: 0;
    font-family: 'Poppins', sans-serif;
    background: var(--background-color);
    color: var(--text-color);
}

/* --- MAIN LAYOUT --- */
main {
    padding: 20px;
    max-width: 1200px;
    margin: auto;
}

.dashboard-grid {
    display: flex;
    gap: 30px;
    margin-top: 15px;
}

.left-column {
    flex: 2; /* Takes up 2/3 of the space */
}

.right-column {
    flex: 1; /* Takes up 1/3 of the space */
}

/* --- HEADER AND MENU --- */
.header {
    background: var(--main-green);
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: white;
    border-radius: 12px 12px 0 0;
    position: relative;
}

.logo-container {
    display: flex;
    align-items: center;
    gap: 10px;
}

.logo {
    height: 45px;
    width: auto;
    object-fit: contain;
}

.logo-text h2 {
    margin: 0;
    font-size: 24px;
    line-height: 1;
}

.logo-text small {
    font-size: 10px;
}

.menu-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 10px;
}

.menu-btn .bar {
    display: block;
    width: 28px;
    height: 4px;
    background: #ffc940; /* Yellow accent */
    margin: 4px 0;
    border-radius: 2px;
    transition: 0.3s;
}

.menu-dropdown {
    position: absolute;
    top: 70px;
    right: 20px;
    background: white;
    border-radius: 10px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
    padding: 10px 0;
    width: 180px;
    display: none; /* Controlled by JavaScript */
    z-index: 1000;
}

.menu-dropdown.open {
    display: block;
}

.dropdown-item {
    display: flex;
    align-items: center;
    padding: 12px 18px;
    font-size: 16px;
    font-weight: 400;
    color: var(--text-color);
    text-decoration: none;
    transition: background 0.2s ease;
    gap: 10px;
}

.dropdown-item:hover {
    background: #f4f4f4;
}

.dropdown-item.logout {
    color: #b30000;
}

/* --- TITLES --- */
.page-title {
    font-size: 30px;
    color: #2d4f1f;
    margin-top: 20px;
    margin-bottom: 5px;
}

.date {
    color: #444;
    margin-top: 0;
}

/* --- CARDS GENERAL --- */
.card {
    background: white;
    border-radius: 12px;
    padding: 18px;
    margin-top: 20px;
    box-shadow: 0 3px 8px rgba(0,0,0,0.1);
}

/* --- MOOD SECTION --- */
.mood-card {
    background-color: #d1ead6; /* Light green background from image */
}

.mood-card h3 {
    text-align: center;
    margin-top: 0;
    color: #235016;
}

.mood-options {
    display: flex;
    justify-content: space-around;
    margin-top: 20px;
}

.mood-item {
    text-align: center;
    cursor: pointer;
    padding: 5px;
    border-radius: 10px;
    transition: 0.25s ease;
}

.mood-item:hover {
    background-color: rgba(255, 255, 255, 0.5);
}

.mood-item.selected {
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
    transform: scale(1.05);
}

.mood-circle {
    font-size: 36px; /* Size of the emoji */
    width: 80px;
    height: 80px;
    border-radius: 50%;
    margin: auto;
    margin-bottom: 10px;
    border: 4px solid;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.25s ease;
}

/* Mood Circle Colors */
.happy .mood-circle { border-color: var(--happy-color); }
.neutral .mood-circle { border-color: var(--neutral-color); }
.tired .mood-circle { border-color: var(--tired-color); }
.stressed .mood-circle { border-color: var(--stressed-color); }


/* --- INFO CARDS --- */
.info-row {
    display: flex;
    gap: 15px;
    margin-top: 20px;
}

.info-card {
    flex: 1;
    background: white;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.info-card h4 {
    background: var(--light-green);
    color: white;
    padding: 8px;
    border-radius: 8px;
    font-size: 15px;
    margin-top: 0;
}

.info-card p {
    margin: 5px 0;
    font-size: 16px;
}

.note {
    font-size: 12px;
    color: #777;
}

/* --- EMOTIONAL WELLNESS --- */
.emotional-card {
    background-color: #d1ead6; /* Light green background from image */
    padding: 25px 18px;
}

.emotional-card h4 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #235016;
}

.stress-container {
    margin-bottom: 10px;
}

#stressSlider {
    width: 100%;
    -webkit-appearance: none;
    height: 8px;
    background: #ccc;
    outline: none;
    opacity: 0.7;
    transition: opacity .2s;
    border-radius: 4px;
}

.stress-labels {
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    color: #333;
    margin-top: 2px;
}

.energy-note {
    color: #777;
    font-size: 14px;
    text-align: center;
    margin-top: 15px;
}

.submit-btn {
    background: #2f6d25;
    color: white;
    padding: 15px;
    border-radius: 10px;
    border: none;
    font-size: 18px;
    width: 100%;
    cursor: pointer;
    margin-top: 20px;
    transition: background 0.3s ease;
}

.submit-btn:hover {
    background: #3c8832;
}


/* --- WEEKLY SUMMARY --- */
.weekly-card {
    min-height: 400px; /* Ensure card is visible */
}

.weekly-card h3 {
    text-align: center;
    margin-top: 0;
    color: #235016;
}

#weekRange {
    text-align: center;
    font-size: 14px;
    color: #555;
}

.chart {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    height: 180px;
    margin: 20px 0 10px 0;
    padding: 0 10px;
}

.bar {
    width: 10%; /* Adjust width for 7 bars */
    border-radius: 5px 5px 0 0;
    transition: height 0.5s ease;
}

/* Bar Colors based on provided CSS */
.sun { background: #2f682f; }
.mon { background: #9ac35c; }
.tue { background: #ffe36e; }
.wed { background: #ff9c28; }
.thu { background: #b4d9ea; }
.fri { background: #2f682f; }
.sat { background: #6c8f45; }

.chart-labels {
    display: flex;
    justify-content: space-between;
    padding: 0 10px;
    font-size: 12px;
    color: #555;
    margin-bottom: 20px;
}

.freq {
    text-align: center;
    font-size: 14px;
}

.tip-section {
    padding-top: 15px;
    border-top: 1px dashed #ccc;
    margin-top: 20px;
}

.tip-title {
    font-weight: 600;
    font-size: 16px;
    color: #235016;
}

.tip {
    font-style: italic;
    color: #555;
    margin-top: 5px;
}

/* --- RESPONSIVENESS --- */
@media (max-width: 900px) {
    .dashboard-grid {
        flex-direction: column;
    }

    .info-row {
        flex-direction: column;
        gap: 10px;
    }

    .left-column, .right-column {
        flex: 1;
    }

    .mood-options {
        flex-wrap: wrap;
    }

    .mood-item {
        margin-bottom: 15px;
    }
}