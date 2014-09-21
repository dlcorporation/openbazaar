# Contributing to OpenBazaar

OpenBazaar is an open source project. We love contributions. We would like to
work more *[bazaar](http://www.catb.org/esr/writings/cathedral-bazaar/)-style*
and encourage external authors. Thanks for your interest in contributing.
You're amazing!

This document outlines some contribution guidelines so that your contributions
can be included in the codebase.

## Workflow
To contribute, follow these simple steps:

1. [Fork](https://help.github.com/articles/fork-a-repo) the GitHub repo.
1. [Clone your fork](https://help.github.com/articles/fork-a-repo#step-2-clone-your-fork):

   ```
   git clone git@github.com:*your-username*/OpenBazaar.git
   ```
1. [Configure remotes](https://help.github.com/articles/fork-a-repo#step-3-configure-remotes)
   so that you can merge back from `upstream`.

   ```
   git remote add upstream https://github.com/OpenBazaar/OpenBazaar.git
   ```
1. Find an [issue](https://github.com/OpenBazaar/OpenBazaar/issues)
that you want to fix.
1. [Create a new branch](http://git-scm.com/book/en/Git-Branching-Basic-Branching-and-Merging)
   in your clone (off of the `develop` branch):

   ```
   git checkout develop
   git checkout -b *my_feature*
   ```
1. Write tests for your fix.
1. Implement your fix.
1. Make sure the build passes:

   ```
   make
   ```
1. Push your new branch with your changes to your fork:

   ```
   git push origin *my_feature*
   ```
1. [Submit](https://github.com/github/hub) a pull request to `develop`:

   ```
   hub pull-request
   ```

Be careful:
* Do not work on the main OpenBazaar GitHub repo directly, even if you are
a collaborator.
* Do not work directly on your local `develop` or `master` branches.
* Do not branch off of the `master` branch.

You should never need to touch the `master` and `develop` branches on your local
machine or on your personal GitHub repo directly. When you want to update them,
simply pull from `upstream` and push to your `origin`.

## Finding an issue
There are a few ways to find something to do on the project:

1. **You want to implement a feature we're already planning**. Great! We don't
yet have a detailed roadmap, but we're working on having one on our wiki. For
now, visit us on #openbazaar on IRC so that we can tell you about our plans.
You may also find some discussion on the feature/plan in one of the
[issues](https://github.com/OpenBazaar/OpenBazaar/issues) (try the
`help wanted` tag). Mention that you'll be working on it (or assign it to
yourself if you're a collaborator). If someone else is working on it, please
collaborate with them; they may need your help and we don't want to do the same
work twice. If you cannot find any such issue, please open a new one and
publish your thoughts. If the issue is heavy on the technical side, do not
forget to include any useful links (RFCs, Wikipedia entries, StackOverflow
posts, mailing list threads – you get the idea).

1. **You have an idea about a new feature**. Please go ahead and implement it!
It may well be something we haven't thought about – thanks for enriching our
codebase. Nevertheless, before embarking on your project, please talk to us
on #openbazaar on IRC. This is important, because we may already have plans
for a feature of this kind. In that case, the plans may detail how we envision
to build your idea and you may want to follow these plans or at least discuss
them with us.

1. **You have found a bug**: Reporting bugs is extremely valuable to us. Please
proceed directly to the
[issues page](https://github.com/OpenBazaar/OpenBazaar/issues?state=open)
and check if someone is experiencing the same problem as you. If not, open
a new issue including:
  * Your hardware and software architecture (e.g. "I am using OpenBazaar
Beta 2.0 on Debian wheezy 64-bit over Python 2.7.6"). If you are on a Unix-
flavored system, the following commands may help you:

       ```
       python --version
       uname -ar
       ```
  * How you installed our project. Did you `git-clone` the nightly, did you
attempt to install it via the debian package, did you do a hybrid setup?
  * What error you are observing. Does the system crash with an exception,
(which one?), does it hang (please provide a screenshot if relevant), does
it do something quirky?
  * A copy of the project logs. These can be found in the `logs/production.log`
folder. Logs are extremely useful. Please make a
[gist](https://gist.github.com/) with your log and provide a link in your
report.

1. **You have a found a bug you can fix or some other problem in the code**:
Maybe the project is not yet working on your favourite hardware or software
architecture; maybe a bug in our codebase may be causing too much trouble;
perhaps you'd like to see the project uphold to higher standards before you
use it. We definetely want your input on this! If you feel your programming
skills and your understanding of the project is sufficient, we will be glad
if you helped us. Just go to the
[open issues page](https://github.com/OpenBazaar/OpenBazaar/issues?state=open),
pick an issue that you think is worthy, and start working on it. Leave a
comment indicating your intention or assign the issue to yourself. Double-check
that no one else is doing the same work; if they are, please collaborate!
If the issue is new and you manage to fix it, then please submit
the issue and the patch in the form of a Pull Request. See the
[Workflow](https://github.com/OpenBazaar/OpenBazaar/blob/master/CONTRIBUTING.md#workflow)
and the
[Reviewing Pull Requests](https://github.com/OpenBazaar/OpenBazaar/blob/master/CONTRIBUTING.md#reviewing-pull-requests)
sections for details on how to go about it. Once again,
thank you for contributing!

1. **Look at the code and see if you can refactor something**. Look for
[broken windows](http://pragmatictips.com/4). [pylint](http://www.pylint.org/)
can sometimes be a good guide.

Please be bold in your pull requests. If you have a big idea, you're very
welcome to create an issue and bring it up for discussion.

## Branching and releases

We use [a successful git branching model](http://nvie.com/posts/a-successful-git-branching-model/).
We maintain two branches on our main repo: `master` and `develop`. `master`
contains stable code that users are expected to pull and run. It is our most
recent release targeting end-users. `develop` contains code currently under
development which has passed reviews and is scheduled for the next release
cycle.

We don't usually maintain other branches on the main repo, unless there is
some special occasion.

On every release cycle, which is approximately every 4 weeks, we merge from
`develop` onto `master` and create a release commit. We may also do this more
often if there are important security issues or critical bug fixes. Commits on
`master` are [tagged](http://git-scm.com/book/en/Git-Basics-Tagging) with
release numbers, and the tags are GPG-signed by
[dionyziz' key](http://pgp.mit.edu/pks/lookup?op=vindex&search=0x2DA450F3AFB046C7)
whose fingerprint is given below:

```
45DC 00AE FDDF 5D5C B988  EC86 2DA4 50F3 AFB0 46C7
```

As an example, see the
[Beta 1.0 tag](https://github.com/OpenBazaar/OpenBazaar/tree/v0.1.0).

## Security
OpenBazaar is security-related software. We make heavy use of cryptography and
the blockchain. We employ
[Ricardian contracts](https://github.com/OpenBazaar/OpenBazaar/wiki/Contracts-and-Listings),
2-of-3 [multisig](http://bitcoin.stackexchange.com/a/3729/1587),
[proof-of-burn](https://blog.openbazaar.org/proof-of-burn-and-reputation-pledges/),
trust-as-risk,
[webs-of-trust](https://gist.github.com/dionyziz/e3b296861175e0ebea4b),
anonymity-preserving transport layers, and other features that are of critical
importance to the network.

We take our users' security and anonymity seriously, and it is our first priority
to protect them.

As such, we require certain code quality from contributors. Auditing of software
is much more efficient when the code is clear, simple, modular, and orthogonal.
Therefore, we may be stricter in our pull request reviews than you may be used to
from other software projects. This is intentional.

This does not mean we don't appreciate your patches. On the contrary, we appreciate
your work enough to devote time to review it in depth and ensure it is of good quality when it
gets merged.

## Reviewing pull requests
If you make a pull request with your change, we promise to review it within
3 days. Hopefully we will review it within 1 day – we try to be responsive.

Reviewing means you'll either get a comment with a request to change something,
or we'll merge your pull request. If we request a change and you make it, we'll
review you again.

Pull requests are reviewed by our peers, just like you. You can also review
pending pull requests by others too! Just go to 
[the list of open pull requests](https://github.com/OpenBazaar/OpenBazaar/pulls),
pick one you want to see merged, and see if the code looks good. If you see
some issue, leave a comment on the particular line of code, or on the pull
request itself. If everything looks good to you, leave a comment indicating
that it's ready to be merged. You can say "LGTM" for "Looks Good To Me". If
you're a collaborator, you can also merge pull requests directly in this case.

Try to make one pull request per issue. If you want to make two changes,
make *two* different branches from `develop` and pull request. If multiple
changes depend on each other, then you should *still* make a different branch
for each change – but base the dependent branch on the branch it depends on
instead of `develop`. After you make your changes, you should make two different
pull requests. First, make a pull request from the base branch (that the other
branch was based on). Finally, make a pull request for the dependent
branch.
Write a comment on your pull request of the dependent branch saying it depends
on a previous pull request by
[mentioning](https://github.com/blog/957-introducing-issue-mentions) the
previous pull request. We'll then review them in order.

If a pull request fixes an issue, mention the issue it fixes in your pull
request description or in one of your commit messages, such as "Fix #007".
When the pull request is merged, you can close the issue too.

**Please don't merge your own pull requests!** Peer review exists to ensure our
software is of good quality. Even the most experienced programmers make
mistakes. It's important that the code is seen by at least the person who
wrote it and someone else.

Also, never push directly to the `upstream` repo, only your fork. All code changes
**must** go through pull requests.

Again, please note that we merge to `develop`, not directly to `master`.
The `master` branch is reserved for stable releases, and we update it on
every release cycle, or for important security fixes or other critical bug fixes.

`develop` is our working branch. Anything that is merged into `develop` will be
deployed to production within the next release cycle.

If you want to show your work to others, but your pull request is not yet ready
for merging, please prefix its title with `[WIP]`, indicating that it is a
*work in progress*. We won't merge work-in-progress pull requests until the
indicator is removed from the title.

## Requirements
We try to ensure the quality of the code we merge is decent. Here are
some things we look for:

1. The change fixes **a real problem**, introduces a new feature, or usefully
refactors existing code. We look for the GitHub issue it corresponds to to see
that it really does fix the problem. If it's a new feature, we make sure it
follows our overall vision for OpenBazaar.

1. The change **fixes one problem** and not multiple problems.
Or that it introduces one feature, not multiple. If the pull request can be
split up to multiple ones, we'll ask you to do so. If it's one big feature,
you may want to split it up into several pull requests introducing it
partially so that reviews can be expedited.

1. **The change is architecturally sound.** We want to keep our code organized
based on correct software design principles and maintain modularity,
extensibility, and orthogonality. We also value simplicity and elegance and
want to make sure we don't overabstract.

1. **The change is tested.** We are starting to include tests for our code
changes, especially in back-end code. While most of our code is currently
untested, we may ask you to write tests for new code. We do this so that new
code is tested and eventually unit tests can be written for the old code as
well. That way, we don't decrease our coverage and we don't introduce new but
untested code. Ideally, you should make sure all use cases are covered. This
doesn't include just all lines of code, but also all the categories of use
cases you can think of. This is not a strict policy yet, but in the future we
may not merge code that doesn't include unit tests. If you make a bug fix, we
suggest a
[regression test](https://en.wikipedia.org/wiki/Regression_testing#Background).
We recommend that you follow
[test-driven development](https://en.wikipedia.org/wiki/Test-driven_development)
principles and write tests before you implement.

1. **The tests pass.** This includes tests that were not written for the
specific change – all tests must pass. We do not merge a failing build. You can
run all tests using `make`.  We use
[travis](https://travis-ci.org/OpenBazaar/OpenBazaar)
to automatically run tests on every pull request and on every merge. You should
also enable it on your fork so that tests run after each push.

1. **Screenshots are included.** We currently don't automatically test
front-end code. However, we ask you to provide a screenshot with any front-end
change you make. This includes HTML, CSS, and JS changes. If you're fixing a
front-end bug, please upload a screenshot of the buggy situation as well as the
fixed situation. If it's a new feature, include a screenshot of how it looks at
every state. These screenshots can be included in a pull request comment.

1. **Coding style guidelines are followed.** We're pretty strict about coding
style and will not merge until you fix formatting issues. This ensures
consistency across our codebase. We follow
[pep8](http://legacy.python.org/dev/peps/pep-0008/) in our Python code, and
[JSHint](http://www.jshint.com/) for our Javascript. Our build includes tests
for style conformance so that you have some guidance about formatting.

1. **Your commits are clean.** If you have commits that you've used for
debugging purposes and for style fixes, these must be interactively rebased
and potentially squashed. We will ask you to do that before we're ready to
merge you. Your commit messages should also be descriptive.

1. **Your branch is rebased onto `develop`.** If changes by others have been
merged into `develop` since your pull request, you must
[rebase](http://git-scm.com/book/ch3-6.html) your branch onto `develop` before
we can merge your branch. We have many external contributors. To achieve a
cleaner history, **we prefer rebasing over merging**.

1. **You have sufficiently documented your code**. If a lot of code is
affected by your pull request, make sure it is commented; follow your
judgement on what needs explaining and make sure the code and the comments
match. Please include [docstrings](https://en.wikipedia.org/wiki/Docstring)
in all of the important new functions or classes.

1. **You have a nice pull request**. While we do not strictly require it,
we urge you to accompany your pull request with a comprehensive description:
  * what does it change or fix (Changelog)
  * why did you do it (Motivation)
  * how can we use the new features (Usage guide)
  * how should we further develop it (Roadmap)
  * etc

 The description does neither have to be lengthy nor contain all of the above;
it just has to be structured and clear. Consider your pull request
description as documenting the evolution of our codebase; anyone who seeks to
find if a feature has been implemented or a bug has been fixed should be able
to read the pull request and feel certain that this is the case without having
to resort to the code.


## Commit access
If you contribute often and become a trusted member of our team, we may give
you commit access so that you can assign issues to yourself, have issues
assigned to you, or merge pull requests by others. Please follow the
guidelines above.

Please note that because OpenBazaar is security-related software, we are
reluctant to give contributor access to too wide a range of committers. Don't
take it personally – this doesn't mean we don't appreciate your efforts, just
that we're especially diligent when it comes to security.

## License
We're an open source project. We release our code under the
[MIT license](https://en.wikipedia.org/wiki/MIT_License).
By contributing to the project, you are agreeing to make your
modifications available to the world for ever, even if you change your mind
later.

[See the full license](https://github.com/OpenBazaar/OpenBazaar/blob/master/LICENSE.md)
for more information.

## Communications
We maintain a [blog](https://blog.openbazaar.org/). Check back often for
important release and feature announcements.

We don't often use a development mailing list like most open source projects.
The best way to reach the development team is through IRC, on #openbazaar at
Freenode.

We also have an [OpenBazaar twitter account](https://twitter.com/openbazaar)
and a very active [OpenBazaar subreddit](https://reddit.com/r/openbazaar)
which is an excellent place to ask questions and get answers. We encourage
you to post there and, if you're a more experienced contributor, to answer any
questions users may have.
