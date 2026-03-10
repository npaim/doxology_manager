(function(){
  function build(){
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl || !window.FullCalendar) return false;
    if (calendarEl.__inited) return true;
    calendarEl.__inited = true;

    const tt = (k, dflt) => (window.I18N ? I18N.t(k) : dflt);

    const calendar = new FullCalendar.Calendar(calendarEl, {
      locale: (window.I18N && I18N.getLang() === 'pt-br') ? 'pt-br' : 'en',
      initialView: 'dayGridMonth',
      height: 'auto',
      fixedWeekCount: false,
      events: '/api/services',
      buttonText: { today: tt('today','Today'), month: tt('month','Month'), week: tt('week','Week'), day: tt('day','Day') },
      dateClick: function(info){ window.location = '/services/new?date=' + info.dateStr; },
      eventClick: function(info){ const id = info.event.id; window.location = '/services/' + id; },
      eventContent: function(info){
        let props = info.event.extendedProps;
        return { html: `
          <div class="text-center">
            <div class="font-semibold text-sm">${(props.start_time && props.end_time ? `${props.start_time} — ${props.end_time}` : (props.start_time || props.end_time || '')) || ''}</div>
            <div class="text-xs text-gray-600">${props.preacher || ''}</div>
          </div>` };
      },
      eventDidMount: function(info){
        let props = info.event.extendedProps;
        const tooltip = document.getElementById('tooltip');
        info.el.addEventListener('mouseenter', function(){
          tooltip.innerHTML = `
            <div class="tooltip-content">
              <div class="tooltip-time">${(props.start_time && props.end_time ? `${props.start_time} — ${props.end_time}` : (props.start_time || props.end_time || '')) || '-'}</div>
              <div><b>${tt('preacher','Preacher')}:</b> ${props.preacher || '-'}</div>
              <div><b>${tt('leader','Leader')}:</b> ${props.leader || '-'}</div>
              <div><b>${tt('sermon_title','Sermon Title')}:</b> <i>${props.title || '-'}</i></div>
              <div><b>${tt('notes','Notes')}:</b> <i>${props.notes || ''}</i></div>
            </div>`;
          tooltip.style.display = 'block';
        });
        info.el.addEventListener('mousemove', function(e){ tooltip.style.left = (e.pageX + 15) + 'px'; tooltip.style.top = (e.pageY + 15) + 'px'; });
        info.el.addEventListener('mouseleave', function(){ tooltip.style.display = 'none'; });
      }
    });

    calendar.render();
    window.onLanguageChanged = function(lang){ try { calendar.setOption('locale', (lang==='pt-br'?'pt-br':'en')); calendar.setOption('buttonText', { today: tt('today','Today'), month: tt('month','Month'), week: tt('week','Week'), day: tt('day','Day') }); } catch(_){} };
    return true;
  }

  function init(){
    if (build()) return;
    let tries = 0; const timer = setInterval(function(){ tries++; if (build() || tries > 20) clearInterval(timer); }, 100);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

