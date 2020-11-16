$(document).ready(() => {
  init_confirm_follow()
  init_dtps()
  render_search()
  render_selects()

  if (window.url === '/archive') {
    $('#id_reference').change(function () {
      const $this = $(this)
      window.location = window.url + '?ref=' + $this.val()
    })
  }
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
    minimumInputLength: 2,
    allowClear: false,
    placeholder: 'Click to select a company',
    theme: 'bootstrap4',
    width: '100%',
  })
  $('#search-btn').click(function (e) {
    e.preventDefault()
    $.post(window.price_url, {company: $('#id_company').val(), date: $('#id_date').val()})
      .done((data) => {
        if (data.length === 1) {
          data = data[0]
          $('#id_high').val(data['High'])
          $('#id_low').val(data['Low'])
          $('#search-form').submit()
        } else {
          bootbox.prompt({
            title: 'Choose a value',
            message: "<p>You've selected a day on the weekend, so you have the choice of taking Friday or Monday's pricing:</p>",
            inputType: 'radio',
            inputOptions: [
              {
                  text: `Friday ${data[0]['Date']}: ${data[0]['Low']} - ${data[0]['High']}`,
                  value: 0,
              },
              {
                  text: `Monday ${data[1]['Date']}: ${data[1]['Low']} - ${data[1]['High']}`,
                  value: 1,
              },
            ],
            callback: function (result) {
              if (result) {
                $('#id_high').val(data[result]['High'])
                $('#id_low').val(data[result]['Low'])
                $('#search-form').submit()
              }
            }
          })
        }
      })
      .fail(function (xhr, text, error) {
        console.log(xhr)
        console.log(text)
        console.log(error)
      })
  })
}

const render_selects = () => {
  const selects = $('select').not('.select2-offscreen').attr('autocomplete', 'off').not('.select2-heavy')
  selects.each((i, el) => {
    const $el = $(el)
    $el.val(el.dataset.initial)
    $el.select2({
      placeholder: $el.attr('placeholder'),
      allowClear: true,
      theme: 'bootstrap4',
      width: '300',
    })
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
