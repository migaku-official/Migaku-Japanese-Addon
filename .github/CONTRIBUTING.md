# Contributing to the MIA Japanese Support Addon 

<!-- If you change any of the headings in this document, remember to update the table of contents. -->
- [How Can I Contribute?](#how-can-i-contribute)
- [Issue Search and Tagging](#issue-search-and-tagging)
- [Contribution Guides](#contribution-guides)
- [Writing Commit Messages](#writing-commit-messages)
- [Tips](#tips)

## How Can I Contribute?
Fork the repository onto your Github account, create a separate branch to commit changes to, then submit a pull request
### Issue Search and Tagging
If you're looking for issues to work on, a good place to start is with tickets labeled [high priority](https://github.com/processing/p5.js-web-editor/labels/priority%3Ahigh). You can also look for tickets that are [feature enhancements](https://github.com/processing/p5.js-web-editor/labels/type%3Afeature), [bug fixes](https://github.com/processing/p5.js-web-editor/labels/type%3Abug), and a few other tags. 

If you feel like an issue is tagged incorrectly (e.g. it's low priority and you think it should be high), please update the issue!

### Contribution Guides

* [https://guides.github.com/activities/hello-world/](https://guides.github.com/activities/hello-world/)
* [https://guides.github.com/activities/forking/](https://guides.github.com/activities/forking/)

## Writing Commit Messages

Good commit messages serve at least three important purposes:

* They speed up the reviewing process.
* They help us write good release notes.
* They help future maintainers understand your change and the reasons behind it.

Structure your commit message like this:

 ```
 Short (50 chars or less) summary of changes ( involving Fixes #Issue-number keyword )

 More detailed explanatory text, if necessary. Wrap it to about 72
 characters or so. In some contexts, the first line is treated as the
 subject of an email and the rest of the text as the body. The blank
 line separating the summary from the body is critical (unless you omit
 the body entirely); tools like rebase can get confused if you run the
 two together.
 ```

* Write the summary line and description of what you have done in the imperative mode, that is as if you were commanding someone. Start the line with "Fix", "Add", "Change" instead of "Fixed", "Added", "Changed".
* Always leave the second line blank.
* Be as descriptive as possible in the description. It helps reasoning about the intention of commits and gives more context about why changes happened.

## Tips

* If it seems difficult to summarize what your commit does, it may be because it includes several logical changes or bug fixes, and are better split up into several commits using `git add -p`.