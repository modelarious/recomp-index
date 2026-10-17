# Origin

Raw capture of the exact originating user request. Written once at provisioning time; treat as immutable evidence.

- Request ID: `home-service-template-20260918-v1`
- Client: ChatGPT with GitHub connector
- Conversation URL: UNKNOWN (not supplied; never invented)

## Exact raw user request (verbatim)

```
yeah, unlazy feels like it should be on by default, it's so extremely useful to the point of practically being manditory



Alright, I validated that I can access home.lan and it looks exactly like what I would want.  So now I want the auto deploy pipeline.  I'm not sure how in the world to configure this, but the pieces I for sure need:

- auto-discovery. When we build a new project, there should be no need to add an entry into the home website repo to get it to find the new project, instead we should operate on a model of: template repo that has the mechanism built in already that allows it to build, tag, and push to the location that's useful for our home website to pick up automatically.  And it crucially includes all the relevant information needed to display a card on home.lan so that home.lan can essentially be ambivalent to all the project work going on.  It's essentially meant as a ui layer to show things that we have built and put in the right spot
- free: if this system depends on automation that is limited by a free plan, it will silently fail and make things terrible.  Either a generous free tier that is capable of handling at least 1000 builds per month, or a combination of multiple free tiers used in a clever way to distribute the load across multiple services. You of course have full rights to use my github credentials on music mac to do whatever you need to accomplish this.  They should essentially give you full access to do what you need to do.
- monitored. home.lan should have a status page that I can see basically red/yellow/green for each service supporting home.lan and how healthy it is.  For example, if we see that there have been new pushes to our projects that didn't get built and tagged and moved, that is a red status.  It should give me a clear and immediate picture of if I can trust home.lan to be up to date or not.  This monitor should also be able to auto discover the projects in our github that are using the specific setup that allows them to push to be displayed in home.lan.  This status page should complain loudly in a way that is hard to ignore if something is failing instead of just degraded. I shouldn't have to open it to find out there is a critical error.



use unlazy to achieve this, and describe in extremely simple and clear terms to me, once you finish, exactly how this works as well as any sources of money spend that could be involved, any limitations that might restrict things and just plainly tell me any restrictions or issues with the system. I value clear communication above project completion. We can always go for another round.
```
