(function(){
  function build(){
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl || !window.FullCalendar) return false;
    if (calendarEl.__inited) return true;
    calendarEl.__inited = true;

    const tt = (k, dflt) => (window.I18N ? I18N.t(k) : dflt);
    const tooltip = document.getElementById('tooltip');

    function positionTooltip(e){
      if (!tooltip) return;
      const gap = 14;
      const rect = tooltip.getBoundingClientRect();
      const width = rect.width || 280;
      const height = rect.height || 140;
      const maxLeft = window.innerWidth - width - gap;
      const maxTop = window.innerHeight - height - gap;
      let left = e.clientX + gap;
      let top = e.clientY + gap;

      if (left > maxLeft) left = Math.max(gap, e.clientX - width - gap);
      if (top > maxTop) top = Math.max(gap, e.clientY - height - gap);

      tooltip.style.left = left + 'px';
      tooltip.style.top = top + 'px';
    }

    const calendar = new FullCalendar.Calendar(calendarEl, {
      locale: (window.I18N && I18N.getLang() === 'pt-br') ? 'pt-br' : 'en',
      initialView: 'dayGridMonth',
      height: 'auto',
      fixedWeekCount: false,
      events: '/api/services',
      buttonText: { today: tt('today','Today'), month: tt('month','Month'), week: tt('week','Week'), day: tt('day','Day') },
      dateClick: function(){},
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
        info.el.addEventListener('mouseenter', function(e){
          if (!tooltip) return;
          tooltip.innerHTML = `
            <div class="tooltip-content">
              <div class="tooltip-time">${(props.start_time && props.end_time ? `${props.start_time} — ${props.end_time}` : (props.start_time || props.end_time || '')) || '-'}</div>
              <div><b>${tt('service_template','Service Template')}:</b> ${props.template_name || '-'}</div>
              <div><b>${tt('preacher','Preacher')}:</b> ${props.preacher || '-'}</div>
              <div><b>${tt('leader','Leader')}:</b> ${props.leader || '-'}</div>
              <div><b>${tt('sermon_title','Sermon Title')}:</b> <i>${props.title || '-'}</i></div>
              <div><b>${tt('notes','Notes')}:</b> <i>${props.notes || ''}</i></div>
            </div>`;
          tooltip.style.display = 'block';
          positionTooltip(e);
        });
        info.el.addEventListener('mousemove', positionTooltip);
        info.el.addEventListener('mouseleave', function(){
          if (!tooltip) return;
          tooltip.style.display = 'none';
        });
      }
    });

    function updateLanguage(lang){
      try {
        calendar.setOption('locale', (lang === 'pt-br' ? 'pt-br' : 'en'));
        calendar.setOption('buttonText', {
          today: tt('today', 'Today'),
          month: tt('month', 'Month'),
          week: tt('week', 'Week'),
          day: tt('day', 'Day')
        });
      } catch(_) {}
    }

    calendar.render();
    document.addEventListener('dm:language-changed', function(event){
      updateLanguage(event.detail && event.detail.lang ? event.detail.lang : (window.I18N ? I18N.getLang() : 'en'));
    });
    window.onLanguageChanged = updateLanguage;
    return true;
  }

  function init(){
    if (build()) return;
    let tries = 0; const timer = setInterval(function(){ tries++; if (build() || tries > 20) clearInterval(timer); }, 100);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
