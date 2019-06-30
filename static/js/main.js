$(document).ready(() => {
  init_confirm_follow()
  init_dtps()
  init_search()
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

const init_search = () => {
  const search_source = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: '/search/symbols/?q={query}',
      wildcard: '{query}'
    }
  })

  const EMPTY = `<p id="no-results">No results found.</p>`
  const $spinner = $('#spinner')
  const $search = $('#id_symbol_search')
  $search.typeahead({
      minLength: 2
    },
    {
      source: search_source,
      display: 'name',
      limit: 20,
      templates: {
        empty: EMPTY,
        suggestion: (v) => `<div>
      <div>
        <span class="tag">${v.symbol}</span>
        <b>${v.name}</b>
      </div>
      <small>
        ${v.region} (${v.currency})
      </small>
    </div>`
      }
    }).on('typeahead:selected', (ev, suggestion) => {
      $('#id_symbol').val(suggestion.symbol)
      $('#id_currency').val(suggestion.currency)
      $('#id_name').val(suggestion.name)
  }).on('typeahead:asyncrequest', () => {
    $spinner.show()
  }).on('typeahead:asynccancel typeahead:asyncreceive', () => $spinner.hide())

  // For testing
  // $(document).on('typeahead:beforeclose', (event) => event.preventDefault())
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
