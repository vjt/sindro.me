---
title: "data-confirm-modal: When a User Did Too Much Damage"
date: 2013-07-02
tags: [ruby, rails, javascript, open-source, ifad]
description: "A user at IFAD did too much damage because the browser's confirm() wasn't explicit enough. So I extracted a Bootstrap modal replacement into a gem. 116 lines of JavaScript."
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
This tiny gem grew to 268 stars and 112 forks, with 32 contributors over 7 years. It learned [Bootstrap 3, then 4 with auto-detection](https://github.com/ifad/data-confirm-modal/blob/v1.6.0/vendor/assets/javascripts/data-confirm-modal.js#L12-L33) (v1.6.0), got a [non-Rails mode](https://github.com/ifad/data-confirm-modal?tab=readme-ov-file#without-rails-with-data-attributes-example-b3-example-b4) with `dataConfirmModal.confirm()` callbacks (v1.2.0), an [npm package](https://www.npmjs.com/package/data-confirm-modal) still pulling 3,700 downloads/week (v1.6.2), and kept working with every Rails version through 6.0. The concept became so mainstream that every UI framework now ships its own confirmation dialog component. The [repo](https://github.com/ifad/data-confirm-modal) is still up.
{{< /retrospective >}}

A user at [IFAD](http://www.ifad.org/) did too much damage last week.

Not maliciously — they just clicked through a chain of destructive actions, happily dismissing the browser's `confirm()` dialogs without reading them. Because nobody reads those. They're ugly grey system dialogs that blend into the background of your workflow. Click OK, click OK, click OK — and suddenly half the data is gone.

So I fixed it. And then I extracted the fix into a gem, because this problem isn't specific to our application. Today I'm releasing [data-confirm-modal](https://github.com/ifad/data-confirm-modal) — 116 lines of JavaScript that replace Rails' built-in `confirm()` with a [Bootstrap modal](https://getbootstrap.com/2.3.2/javascript.html#modals).

<!--more-->

## The fix

The concept is dead simple: any Rails link with `data-confirm` already triggers a browser confirmation. My gem intercepts that event and shows a proper Bootstrap modal instead. The title defaults to **"Are you ABSOLUTELY sure?"** — because apparently we needed to be louder.

Drop-in replacement. Zero changes to your existing code. Add the gem, require the JS, and every `link_to "Delete", @thing, confirm: "This will destroy everything"` now pops up a real modal with a title, a body, and two clearly labeled buttons.

```ruby
# Gemfile
gem 'data-confirm-modal', github: 'ifad/data-confirm-modal'
```

```javascript
// application.js
//= require data-confirm-modal
```

That's it.

## The data-verify trick

Here's the feature I'm most proud of. You know how GitHub makes you type the repository name before you can delete it? Same idea:

```erb
<%= link_to "Delete project", project_path(@project),
  method: :delete,
  data: {
    confirm: "This will permanently delete the project and all its data.",
    verify: "DELETE",
    commit: "I understand, delete it"
  } %>
```

The confirm button stays **disabled** until the user types exactly "DELETE" into the input field. No more muscle-memory clicking through destructive actions. If you want to destroy something, you have to prove you mean it.

## How it works

The interesting bit is the [integration with Rails UJS](https://github.com/ifad/data-confirm-modal/blob/09eca28/vendor/assets/javascripts/data-confirm-modal.js#L88-L108). When a `data-confirm` link is clicked, Rails fires a `confirm` event and checks `$.rails.confirm()` to decide whether to proceed. My code temporarily monkey-patches that function:

```javascript
$(document).delegate('a[data-confirm]', 'confirm', function (e) {
  var element = $(this), modal = getModal(element);
  var confirmed = modal.data('confirmed');

  if (!confirmed && !modal.is(':visible')) {
    modal.modal('show');

    // Temporarily replace Rails' confirm function
    var confirm = $.rails.confirm;
    $.rails.confirm = function () { return modal.data('confirmed'); }
    modal.on('hide', function () { $.rails.confirm = confirm; });
  }

  return confirmed;
});
```

Show the modal, swap the confirm function, restore it on hide. When the user clicks the confirm button in the modal, `modal.data('confirmed')` becomes `true`, the original click is re-triggered, and this time `$.rails.confirm` returns `true`. Clean, minimal, no jQuery UI dependency.

## The damage that started it all

The actual incident at IFAD involved a user managing project data in our internal applications. The browser's `confirm()` dialog had become invisible to them — just another speed bump to click past. The data they deleted took significant effort to recover.

The fix in our application was immediate: swap `confirm()` for a modal that demands attention. The extraction into a gem took three commits and six minutes. Sometimes the best open source comes from the worst production incidents.

[Source on GitHub](https://github.com/ifad/data-confirm-modal). [Check it out on JSFiddle](https://jsfiddle.net/zpu4u6mh/). PRs welcome — especially if you've also been burned by `confirm()`.


---

**Open source from the IFAD years:** [ChronoModel](/posts/2012-05-07-chronomodel-time-travel-postgresql/) (2012) • **data-confirm-modal (2013)** • [Hermes](/posts/2013-10-20-hermes-rails-rumble-2013/) (2013) • [Eaco](/posts/2015-02-28-eaco-authorization-ruby/) (2015) • [Heathen → Colore](/posts/2016-01-15-document-pipeline-heathen-colore/) (2016) • [TM → Pontoon](/posts/2018-02-14-translation-memory-pontoon/) (2018) • [ChronoModel 1.0](/posts/2019-04-06-chronomodel-one-dot-zero/) (2019) • [OneSpan 2FA](/posts/2020-09-11-integrating-onespan-2fa-with-ruby/) (2020) • [ansible-wsadmin](/posts/2026-04-11-ansible-wsadmin/) (2026)
