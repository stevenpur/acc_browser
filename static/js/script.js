document.addEventListener('DOMContentLoaded', function() {
    function showLoadingOverlay() {
        document.getElementById('loadingOverlay').style.display = 'block';
    }

    function hideLoadingOverlay() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    async function getIndivList() {
        const response = await fetch('/getIndvList');
        if (!response.ok) {
            throw new Error('getIndivList response was not ok');
        }
        const indvs = await response.json();
        const select_div = document.querySelector('#select_ind');
        indvs.forEach(function(indv) {
            if (select_div.innerHTML === '') {
                select_div.innerHTML = `<option value="${indv}" selected>${indv}</option>`;
            }
            select_div.innerHTML += `<option value="${indv}">${indv}</option>`;
        });
        select_div.addEventListener('change', function(event) {
            console.log('change event for select_ind')
            const indv = event.target.value;
            plot24hrData(indv);
        })
    }

    async function plotAccData(index, is_smooth, div_id) {
        const url = `/plotAcc?param1=${index}&param2=${is_smooth}`
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('getAccData response was not ok');
        }
        const data = await response.json();
        await Plotly.newPlot(div_id, data);
    }
   
    async function get24hrData(indv) {
        showLoadingOverlay();
        const param1 = indv;
        const url = `/get24hr?param1=${param1}`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('get24hr response was not ok');
        }
        const data = await response.json();
        hideLoadingOverlay();
        return data;
    }

    async function plot24hrData(indv) {
        const data = await get24hrData(indv);
        await Plotly.newPlot('allDayActivity', data);
        console.log('fiished plotting')
        document.querySelector('#allDayActivity').on('plotly_click', function(event){
            label = event.points[0].data.name;
            time = event.points[0].x;
            index = event.points[0].customdata[0];
            plotAccData(index, 'False', 'acc_plot');
        })
    }
    
    function getActLabels() {
        const plot_div = document.querySelector('#allDayActivity');
        const labels = plot_div.data.map(function(trace) {
            return trace.name;
        })
        return labels;
    }

    function getActLabelSelect() {
        const labels = getActLabels();
        const select_div = document.querySelector('#select_label');
        labels.forEach(function(label) {
            label_refac = label.replace(/ /g, "_");
            select_div.innerHTML += `
                <div>
                <input type="checkbox" id="check_${label_refac}" name="check_${label_refac}" value="${label}" />
                <label for="check_$label">${label}</label>
                </div>
            `;
        });
    }

    function renderCompare() {
        const selected_labels = document.querySelectorAll('input[type="checkbox"]:checked');
        const plot24data = document.querySelector('#allDayActivity').data;
        const render_div = document.querySelector('#compare_plot');
        const ncol = selected_labels.length;
        const nplot = parseInt(document.querySelector('#compare_num_input').value);
        const is_smooth = document.querySelector('#is_smooth_input').value; 
        // set the number of columns in the grid
        console.log(plot24data)
        render_div.style.gridTemplateColumns = `repeat(${ncol}, 1fr)`;
        render_div.innerHTML = '';
        selected_labels.forEach(function(selected_label) {
            const label = selected_label.value;
            const label_refac = label.replace(/ /g, "_").replace(/\./g, "_");
            render_div.innerHTML += `<div id="compare_col_${label_refac}"><h2>${label}</h2></div>`;
            const current_div = document.querySelector("#compare_col_" + label_refac);
            for (let i=1; i<=nplot; i++) {
                console.log('current div')
                console.log(current_div)
                console.log('creating div for ' + label_refac)
                current_div.innerHTML += `<div id="compare_plot_${label_refac}_${i}"></div>`;
                console.log('created div for ' + label_refac + i)
                const trace = plot24data.find(function(trace) {
                    return trace.name === label;
                });
                // sample from customdata
                console.log(trace.customdata)
                const random_index = trace.customdata[Math.floor(Math.random() * trace.customdata.length)];
                plotAccData(random_index, is_smooth, `compare_plot_${label_refac}_${i}`)

            }
        })
    }

    function opentab(event, id) {
        console.log('#'+id)
        const tabcontent_selected = document.querySelector('#'+id);
        const tabcontents = document.querySelectorAll('.tabcontent');
        tabcontents.forEach(function(tab) {
            console.log('close tab')
            tab.style.display = 'none';
            console.log(tab)
        });
        console.log('open tab')
        tabcontent_selected.style.display = 'block';
        console.log(tabcontent_selected)
    }
    
    getIndivList()
    .then(() => {
        const indv = document.querySelector('#select_ind').value;
        return plot24hrData(indv);
    })
    .then(() => {
        getActLabelSelect();
    })

    document.querySelectorAll('.tablinks').forEach(tab => {
        tab.addEventListener('click', function(event) {
            console.log('tab clicked')
            const tab_id = event.target.id.replace('view_', '');
            console.log(tab_id)
            console.log(event.target)
            opentab(event, tab_id);
        });
    })

    document.querySelector('#compare_render').addEventListener('click', function() {
        renderCompare();
    })

    
                
})
