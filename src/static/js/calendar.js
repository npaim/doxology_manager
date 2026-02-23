document.addEventListener("DOMContentLoaded", function () {

    const calendarEl = document.getElementById("calendar");

    if (!calendarEl) return;

    const calendar = new FullCalendar.Calendar(calendarEl, {

        initialView: "dayGridMonth",

        height: "auto",

        fixedWeekCount: false,

        events: "/api/services",


        /*
        CLICK DAY → DAY VIEW
        */

        dateClick: function(info) {

            window.location =
                "/services/day?date=" + info.dateStr;

        },


        /*
        CLICK SERVICE → EDIT SERVICE
        */

        eventClick: function(info) {

            const id = info.event.id;

            window.location =
                "/services/" + id;

        },


        /*
        SHOW SERVICES INSIDE CELLS
        */

        eventContent: function(info) {

            let props = info.event.extendedProps;

            return {
                html: `
                    <div class="service-event">
                        <div class="service-time">
                            ${props.time || ""}
                        </div>

                        <div class="service-preacher">
                            ${props.preacher || ""}
                        </div>
                    </div>
                `
            };
        },


        /*
        HOVER TOOLTIP
        */


        eventDidMount: function(info) {

            let props = info.event.extendedProps;

            const tooltip = document.getElementById("tooltip");

            info.el.addEventListener("mouseenter", function(e){
            
                tooltip.innerHTML = `
                    <div class="tooltip-content">
                        <div class="tooltip-time">${props.time || "-"}</div>
                        <div><b>Preacher:</b> ${props.preacher || "-"}</div>
                        <div><b>Leader:</b> ${props.leader || "-"}</div>
                        <div><b>Sermon:</b> <i>${props.title || "-"}</i></div>
                        <div><b>Notes:</b> <i>${props.notes || ""}</div>
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