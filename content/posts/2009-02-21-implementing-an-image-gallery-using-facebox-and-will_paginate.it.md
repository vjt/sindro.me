---
date: 2009-02-21T00:00:00Z
title: Implementare una galleria immagini con facebox e will_paginate
tags: [facebox, javascript, jquery, projects, ruby, will_paginate]
categories: [development]
---

Su [VisitaCSA](http://www.visitacsa.it/) stiamo usando
[facebox](http://famspam.com/facebox) di
[defunkt](http://errtheblog.com/) per mostrare le [immagini dei
luoghi](http://www.visitacsa.it/luoghi/chiesa-di-santantonio) in grande.
Facebox e' un ottimo lightbox generico, perche' e' veloce, stabile, si basa su
[jQuery](http://jquery.com/) e ha un'API davvero pulita.

Ma avevamo bisogno di qualcosa in piu' di un semplice lightbox di
visualizzazione, perche' volevamo che i nostri utenti potessero navigare
facilmente tra tutte le immagini, possibilmente senza modificare facebox. La
soluzione si e' rivelata piuttosto semplice, grazie anche al plugin
[`will_paginate`](http://github.com/mislav/will_paginate/wikis) che stavamo
gia' usando. In sostanza si tratta di avere:

- Un model Photo, attrezzato con il metodo `has_attachment`
- Route per le risorse photos (`map.resources :photos, :only => :show` in
  `config/routes.rb`)
- Un metodo `show` nel controller `PhotosController` che chiama `.paginate`
  con un argomento `:per_page` di 1
- Una vista HTML per la risorsa photo, con i controlli di paginazione usando
  l'helper `will_paginate`
- Del codice jQuery che si aggancia ai link di paginazione e fa caricare al
  browser via AJAX la foto successiva direttamente nel facebox.

Ecco il codice rilevante, semplificato rispetto a quello effettivamente
online, perche' il model photo e' in realta' polimorfico (usa STI) e diverse
collezioni sono gestite dal photos controller (foto, volantini, ecc.) per
diversi model, con miniature diverse :P.

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

### Vista [app/views/photos/show.html.erb]

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

La gem [`image_size`](http://imagesize.rubyforge.org/) e' necessaria per
consentire a facebox di allinearsi correttamente al centro della finestra.

### Helper [app/helpers/photos_helper.rb e app/helpers/application_helper.rb]

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

Il [plugin scrollTo](http://plugins.jquery.com/project/ScrollTo) viene usato
qui per scrollare la vista della finestra fino alla cima del facebox.

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

Be', forse dovrei impacchettare tutto questo in un plugin semplice e carino da
usare, ma e' tutto costruito attorno a componenti riutilizzabili, e lo sforzo
necessario per tenerlo aggiornato al momento e' fuori portata per me a causa di
vincoli di tempo. E, sinceramente, ci vedo poco beneficio. E' un hack
"pagina-con-un-elemento-per-pagina", dopotutto :).

Buon divertimento!
