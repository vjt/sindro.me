---
date: 2009-02-21T00:00:00Z
title: Implementing an image gallery using facebox and will_paginate
tags: [facebox, javascript, jquery, projects, ruby, will_paginate]
categories: [development, all]
---

On [VisitaCSA](http://www.visitacsa.it/) we're using
[defunkt](http://errtheblog.com/)'s [facebox](http://famspam.com/facebox) to
show [places images](http://www.visitacsa.it/luoghi/chiesa-di-santantonio) at
large. Facebox is a great general-purpose lightbox, because it is fast, stable,
is based on [jQuery](http://jquery.com/) and has got a really clean API.

But we needed more than a simple display lightbox, because we wanted our users
to navigate easily between all images, possibly without modifying facebox at
all. The solution turned out to be pretty simple, thanks also to the
[`will_paginate`](http://github.com/mislav/will_paginate/wikis) plugin we were
already using. It all burns out to have:

- A Photo model, instrumented with the `has_attachment` method
- Resource routes for photos (`map.resources :photos, :only => :show` in
  `config/routes.rb`)
- A `show` controller method in the `PhotosController` that calls `.paginate`
  with a `:per_page` argument of 1
- An HTML view for the photo resource, that has pagination controls using the
  `will_paginate` helper
- Some jQuery code hooks onto the pagination links and make the browser load
  via AJAX the next photo directly into the facebox.

Here is the relevant code, simplified from what's actually online, because the
photo model is actually polymorphic (using STI) and many different collections
are handled by the photos controller (photos, flyers, etc) for different
models, with different thumbnails :P.

### Model [app/models/photo.rb]

```ruby
class Photo < ActiveRecord::Base
  has_attachment :storage => :file_system, :path_prefix => 'public/photos',
    :processor => 'ImageScience', :thumbs => { :thumb => '600x800' }
end
```

### Controller [app/controllers/photos_controller.rb]

```ruby
class PhotosController < ApplicationController
  layout nil
  before_filter :find_place

  # The photo gallery core is here
  def show
    photo = Photo.find(params[:id])
    page = params[:page] || @place.photos.index(photo) + 1
    @photos = @place.photos.paginate(:per_page => 1, :page => page)
    @photo = @photos.first
  end

  def find_place
    @place = Place.find(params[:place_id])
  end
end
```

### View [app/views/photos/show.html.erb]

```html
<div class="photo">
  <div style="width: <%= photo_width(@photo) %>px; text-align: center;">
    <%= next_photo_link_for @photo, :in => @photos %>
  </div>
  <p><%=h @photo.title %></p>
  <p>
    <%= will_paginate @photos, :prev_label => '&nbsp;', :next_label => '&nbsp;' %>
  </p>
</div>
```

The [`image_size`](http://imagesize.rubyforge.org/) gem is needed to correctly
let facebox align itself to the center of the window.

### Helpers [app/helpers/photos_helper.rb and app/helpers/application_helper.rb]

```ruby
require 'image_size'

module PhotosHelper
  def next_photo_link_for(photo, options = {})
    collection = options.delete(:in)

    if collection && collection.respond_to?(:next_page)
      facebox_image_link_to photo, options.merge(:page => collection.next_page || 1)
    else
      image_tag photo.public_filename(:thumb, :alt => h(photo.title), :title => h(photo.title)
    end
  end

  def photo_width(photo, thumb = nil)
    width = ImageSize.new(File.read(photo.full_filename(thumb))).width rescue nil
    return (width.nil? || width < 370) ? 370 : width
  end
end

module ApplicationHelper
  def facebox_image_link_to(photo, thumb = nil, options = {})                                           
    link_options = {:page => options.delete(:page)}
    options.reverse_update(:title => h(photo.title), :alt => h(photo.title))                            

    link_to(
      image_tag(photo.public_filename(:thumb), options),
      formatted_photo_path(photo, 'html', link_options),
      :rel => 'facebox'                                                                                 
    )
  end 
end
```

The [scrollTo plugin](http://plugins.jquery.com/project/ScrollTo) is used here
to scroll the window view to the top of the facebox.

### Javascript [public/javascripts/application.js]

```javascript
$(document).ready(function() {

  if ($('#facebox').length > 0) {
    $('#facebox div.pagination a, #facebox a[rel*=facebox]').live('click', function() {

      $('#facebox .content').html('<div class="loading"><img src="'+$.facebox.settings.loadingImage+'"/></div>');
      $.get(this.href, null, function(data) { $.facebox.reveal(data); });

      $.scrollTo('#facebox', {offset: -10, duration: 500});

      return false;
    });
  }

});
```

Well, maybe I should to wrap up all this stuff in a simple-and-nice-to-use
plugin, but it’s all built around reusable components, and the effort needed to
keep it up-to-date is currently out of order for me because of time
constraints. And, sincerely, I see little benefit in it. It’s a
“paginate-with-one-item-per-page” hack, after all :).

Have fun!
