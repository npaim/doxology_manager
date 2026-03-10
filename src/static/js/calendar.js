document.addEventListener("DOMContentLoaded", function () {

    const calendarEl = document.getElementById("calendar");

    if (!calendarEl) return;

    const calendar = new FullCalendar.Calendar(calendarEl, {

        initialView: "dayGridMonth",
        height: "auto",
        fixedWeekCount: false,
        events: "/api/services",

        // CLICK DAY → NEW SERVICE FORM (pre-filled date)
        dateClick: function(info) {
            window.location = "/services/new?date=" + info.dateStr;
        },

        // CLICK SERVICE → SERVICE DETAIL
        eventClick: function(info) {
            const id = info.event.id;
            window.location = "/services/" + id;
        },

        // RENDER EVENT CONTENT (time + preacher)
        eventContent: function(info) {
            let props = info.event.extendedProps;
            return {
                html: `
                    <div class="text-center">
                        <div class="font-semibold text-sm">${(props.start_time && props.end_time ? `${props.start_time} — ${props.end_time}` : (props.start_time || props.end_time || "")) || ''}</div>
                        <div class="text-xs text-gray-600">${props.preacher || ''}</div>
                    </div>
                `
            };
        },

        // HOVER TOOLTIP
        eventDidMount: function(info) {
            let props = info.event.extendedProps;
            const tooltip = document.getElementById("tooltip");

            info.el.addEventListener("mouseenter", function(e){
                tooltip.innerHTML = `
                    <div class="tooltip-content">
                        <div class="tooltip-time">${(props.start_time && props.end_time ? `${props.start_time} — ${props.end_time}` : (props.start_time || props.end_time || "")) || '-'}</div>
                        <div><b>Preacher:</b> ${props.preacher || '-'}</div>
                        <div><b>Leader:</b> ${props.leader || '-'}</div>
                        <div><b>Sermon:</b> <i>${props.title || '-'}</i></div>
                        <div><b>Notes:</b> <i>${props.notes || ''}</i></div>
                    </div>
                `;
                tooltip.style.display = "block";
            });

            info.el.addEventListener("mousemove", function(e){
                tooltip.style.left = (e.pageX + 15) + "px";
                tooltip.style.top = (e.pageY + 15) + "px";
            });

            info.el.addEventListener("mouseleave", function(){
                tooltip.style.display = "none";
            });
        }

    });

    calendar.render();

});

