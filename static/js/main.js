$(document).ready(() => {
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
  $('.date-picker').each((i, el) => {
    const $el = $(el)
    const $input = $el.find('input')
    const $init = $('#initial-' + $input.attr('id'))
    $el.datetimepicker({
      icons: icons,
      format: $input.data('format'),
      date: $init.val(),
    })
  })

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
  const $search = $('#id_symbol')
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
    </div>`
      }
    }).on('typeahead:selected', (ev, suggestion) => {
      console.log('Selected company', suggestion)
      $search.val(suggestion.symbol)
  }).on('typeahead:asyncrequest', () => {
    $spinner.show()
  }).on('typeahead:asynccancel typeahead:asyncreceive', () => $spinner.hide())

  // For testing
  $(document).on('typeahead:beforeclose', (event) => event.preventDefault())
})
