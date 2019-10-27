$(document).ready(() => {
  init_confirm_follow()
  init_dtps()
  render_search()
})

const init_dtps = () => {
  const icons = {
    time: 'fa fa-clock',
    date: 'fa fa-calendar',
    up: 'fa fa-chevron-up',
    down: 'fa fa-chevron-down',
    previous: 'fa fa-chevron-left',
    next: 'fa fa-chevron-right',
    today: 'fa fa-square',
    clear: 'fa fa-trash',
    close: 'fa fa-remove'
  }

  $('.date-time-picker').each((i, el) => {
    const $el = $(el)
    const $input = $el.find('input')
    const $init = $('#initial-' + $input.attr('id'))
    $el.datetimepicker({
      icons: icons,
      format: $input.data('format'),
      date: $init.val(),
      maxDate: 'now',
      defaultDate: $input.data('yesterday'),
    })
  })
  $(document).on('mouseup touchend', function (e) {
    let container = $('.bootstrap-datetimepicker-widget')
    if (!container.is(e.target) && container.has(e.target).length === 0) {
      container.parent().datetimepicker('hide')
    }
  })
}


const render_search = () => {
  const $search = $('#id_company')
  if (!$search.length) {
    return
  }
  $search.select2({
    ajax: {
      url: window.symbol_search_url,
      dataType: 'json',
      delay: 400,
      data: function (params) {
        return {
          q: params.term,
        }
      },
      processResults: function (data) {
        return {
          results: $.map(data, (item) => {
            return {
              text: item.text,
              id: item.id,
            }
          })
        }
      },
      cache: true
    },
    minimumInputLength: 3,
    allowClear: false,
    placeholder: 'Click to select a company',
    theme: 'bootstrap4',
    width: '100%',
  })
}


const init_confirm_follow = () => {
  const $el = $(document)
  $el.find('[data-confirm]').click(function (e) {
    let $a = $(this)
    const target = $a.attr('target')
    let link = $a.attr('href')
    let method = $a.data('method') || 'POST'
    e.preventDefault()
    bootbox.confirm({
      message: $a.data('confirm'),
      title: $a.data('confirm-title') || null,
      callback: result => {
        if (result) {
          if (method.toLowerCase() === 'post') {
            let form = $('#post-form')
            form.attr('action', link)
            $.each($a.data(), function (k, v) {
              if (k === 'method') {
                return
              }
              $('<input>').attr({
                type: 'hidden',
                name: k,
                value: v
              }).appendTo(form)
            })
            if (target) {
              window.open(link, target)
            } else {
              form.submit()
            }
          } else {
            document.location.href = link
          }
        }
      }
    })
  })

  $('[data-method="POST"]').not('[data-confirm]').not('.no-submit').click(function (e) {
    const $a = $(this)
    const link = $a.attr('href')
    e.preventDefault()
    if (link === '#') {
      return
    }
    const form = $('#post-form')
    form.attr('action', link)
    for (const [key, value] of Object.entries($a.data())) {
      if (key !== 'method') {
        $('<input>').attr({type: 'hidden', name: key, value: value}).appendTo(form)
      }
    }
    form.submit()
  })
}
