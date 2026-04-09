---
title: "Eaco: The Holder of the Keys of Hades"
date: 2015-02-28
tags: [ruby, rails, postgresql, open-source]
description: "I just extracted an ABAC authorization framework from our internal IFAD app in an 8-day sprint. ACLs are plain hashes, PostgreSQL jsonb does the heavy lifting, and I hit 100% test coverage at 1:33 PM on a Saturday."
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
Eaco reached [v1.0.0](https://github.com/ifad/eaco/tree/v1.0.0) on May 5, 2016 — commit message: "This is v1.0.0. Two years in production." It grew to 54 stars, 8 forks, 240 commits, and ran authorization at IFAD for five more years after that. [Geremia Taglialatela](https://github.com/tagliala) picked it up in 2020 and kept it running on Rails 6.0 and 6.1, then [modernized the CI](https://github.com/ifad/eaco/commit/19) in late 2025. The ABAC-with-hash-ACLs pattern turned out to be exactly right for an organization where access is determined by position, department, and working group — not just "admin or not." The [repo](https://github.com/ifad/eaco) is still online, and the [YARD documentation](https://vjt.github.io/eaco/) is still some of the most thorough I've ever written for a gem.
{{< /retrospective >}}

[Scriptoria](https://github.com/ifad/scriptoria) is an internal workflow application at [IFAD](http://www.ifad.org/) — a UN specialized agency in Rome — and its authorization layer has been annoying me for months. The code works, but it's tangled into the app. Every time we need to add a new role or change who can access what, we're editing application code that shouldn't care about authorization semantics.

So eight days ago I started extracting it. Today I'm releasing the result: [Eaco](https://github.com/ifad/eaco) — an Attribute-Based Access Control framework for Ruby, named after [Eacus](http://en.wikipedia.org/wiki/Aeacus), the holder of the keys of Hades in Greek mythology.

172 commits. Five releases. 100% test coverage. And a Saturday afternoon I'll never get back.

<!--more-->

## Why not Cancan/Pundit/Rolify?

Because they all think about authorization wrong — or at least, wrong for our use case.

Role-based frameworks give you "this user is an admin" or "this user is an editor." That's fine for a blog. At IFAD we need "this user can read this *specific* document because they're a reviewer in the Loans department, or because they occupy the VP position that was granted access, or because they're tagged as an English-language editor." The access is on the *resource*, not on the user. And it's determined by *attributes* of the user, not a single role column.

That's [ABAC](https://en.wikipedia.org/wiki/Attribute-based_access_control) — Attribute-Based Access Control. The resource has an ACL. The ACL says which *designators* (security attributes) grant access at which level. The user has designators harvested from their identity, group memberships, department, position, tags — whatever your organization's structure looks like. The intersection determines access.

## ACLs are just hashes

Here's the radical simplification: an ACL is a plain Ruby `Hash`. Keys are designator strings, values are role symbols:

```ruby
document.acl
#=> #<Document::ACL {"user:10" => :owner, "group:reviewers" => :reader}>
```

That's it. No join tables, no polymorphic associations, no authorization tables with foreign keys pointing everywhere. A hash. Stored as a single `jsonb` column in PostgreSQL.

This means checking access is a hash key lookup. Granting access is setting a key. Revoking is deleting a key. And querying "all documents this user can see" is a single SQL operation using PostgreSQL's `?|` operator:

```sql
WHERE documents.acl ?| array['user:42', 'group:employees', 'tag:english']::varchar[]
```

One query. No joins. No subselects. The database does the set intersection for you.

## The DSL

Authorization rules live in `config/authorization.rb` — one file, declarative, readable by anyone:

```ruby
authorize Document, using: :pg_jsonb do
  roles :owner, :editor, :reader

  permissions do
    reader   :read
    editor   reader, :edit
    owner    editor, :destroy
  end
end

actor User do
  admin do |user|
    user.admin?
  end

  designators do
    user  from: :id
    group from: :groups
    tag   from: :tags
  end
end
```

The `permissions` block is my favorite piece of this entire gem. Watch what happens: `reader :read` defines the reader role with the `:read` permission. Then `editor reader, :edit` *passes the reader role as an argument* — and because `reader` is now a method that returns its permission set, the editor inherits everything the reader can do, plus `:edit`. It's [method_missing as a DSL](https://github.com/ifad/eaco/blob/v0.8.0/lib/eaco/dsl/resource/permissions.rb#L91-L97):

```ruby
def method_missing(role, *permissions)
  if @permissions.key?(role)
    @permissions[role]
  else
    save_permission(role, permissions)
  end
end
```

First call defines the role. Second call returns its permissions. Role inheritance falls out naturally from Ruby's evaluation order. No special inheritance syntax needed.

## Designators

Designators are the bridge between your organization's structure and Eaco's authorization model. They inherit from `String` and look like `"user:42"` or `"group:reviewers"`:

```ruby
class User::Designators::Group < Eaco::Designator
  label "Group"
end
```

The `from: :groups` option in the DSL tells Eaco to call `user.groups` and wrap each result in a `Group` designator. When you check `user.can?(:read, document)`, Eaco harvests all the user's designators, intersects them with the document's ACL keys, and checks if any of the resulting roles have the `:read` permission.

The designator system is completely pluggable. Your organization has departments? Positions? Committees? Matrix reporting structures? Define a designator class, point it at a method, and Eaco handles the rest.

## The PostgreSQL jsonb adapter

This is where the design really pays off. The entire [adapter is 13 lines](https://github.com/ifad/eaco/blob/v0.8.0/lib/eaco/adapters/active_record/postgres_jsonb.rb#L25-L33):

```ruby
def accessible_by(actor)
  return scoped if actor.is_admin?

  designators = actor.designators.map {|d| sanitize(d) }
  column = "#{connection.quote_table_name(table_name)}.acl"

  where("#{column} ?| array[#{designators.join(',')}]::varchar[]")
end
```

`Document.accessible_by(user)` returns a normal ActiveRecord relation — you can chain it with `.where`, `.order`, `.limit`, whatever. Under the hood, PostgreSQL's `?|` operator checks if the jsonb object contains *any* of the given keys. GIN index on the `acl` column and you're done. This query scales to millions of documents.

I also have a CouchDB-Lucene adapter for another IFAD project, but the jsonb one is the star of the show.

## La Guardiana

The authorization check in the [controller](https://github.com/ifad/eaco/blob/v0.8.0/lib/eaco/controller.rb#L92) is guarded by a 48-line ASCII art guardian figure in the source comments. Her name is La Guardiana, and she watches over every `before_filter :confront_eaco` call. Because if you're going to deny access, you should do it with style. (She's not alone — [Ayanami Rei](https://vjt.github.io/eaco/Eaco/Cucumber/World.html) watches over the test suite.)

```ruby
class DocumentsController < ApplicationController
  before_filter :find_document

  authorize :show, [:document, :read]
  authorize :edit, [:document, :edit]

  private
    def find_document
      @document = Document.find(params[:id])
    end
end
```

That's the entire controller integration. Eaco installs a `before_filter`, checks the `@document` instance variable against `current_user.can?(:read, @document)`, and raises `Eaco::Forbidden` if denied. No ceremony.

## The sprint

Eight days. Feb 20, 2:06 AM — [initial commit](https://github.com/ifad/eaco/commit/622aba1). Feb 20, 2:12 AM — "Import Scriptoria's authorization code." Then the extraction began: restructuring into a proper gem, building the DSL, writing the adapters, adding Rails 3.2/4.0/4.1/4.2 support via [Appraisal](https://github.com/thoughtbot/appraisal), and building out the test suite.

[v0.5.0](https://github.com/ifad/eaco/tree/v0.5.0) on Feb 24 — Rails 3.2 support. [v0.6.0](https://github.com/ifad/eaco/tree/v0.6.0) on Feb 27. [v0.7.0](https://github.com/ifad/eaco/tree/v0.7.0) on Feb 28 at 2:57 AM. Then the final push: the "Enterprise Authorization" Cucumber scenario with a full NERVE organization hierarchy (departments, positions, users), more specs, more features, 100% coverage.

```
cc3c2b4  ACHIEVEMENT UNLOCKED: 100% coverage :party:
4a5723a  This is v0.8.0
```

Feb 28, 1:33 PM. Sixty-seven minutes between reaching 100% coverage and tagging the release. Five releases in eight days. Denominazione d'Origine Controllata.

## What it looks like in practice

```ruby
# Check permission
user.can? :read, document  #=> true

# Same check, other direction
document.allows? :read, user  #=> true

# What roles does this user have?
document.roles_of user  #=> [:owner]

# Grant access
document.grant :reader, :group, "reviewers"

# Revoke access
document.revoke :user, 42

# Get all documents this user can access
Document.accessible_by(user)  # => ActiveRecord::Relation
```

Both directions work — `user.can?` and `document.allows?` — because sometimes you're thinking from the user's perspective and sometimes from the resource's. Same logic underneath.

## Made in Italy

The gem is MIT-licensed and [on GitHub](https://github.com/ifad/eaco). The [YARD documentation](https://vjt.github.io/eaco/) covers every public method. The [Cucumber features](https://github.com/ifad/eaco/blob/v0.8.0/features/enterprise_authorization.feature) read like specifications — the Enterprise scenario models a real organizational structure with the complexity you'd expect from a UN agency.

If your authorization needs go beyond "admin or not" — if access depends on *who the user is in relation to the resource* — give Eaco a try. `gem install eaco` and create your `config/authorization.rb`.

The keys of Hades are in good hands.
