# FEDEX PROJECT
The following application simulate the backend of a delivery company like fedex.

## Application Diagram
![Fedex_diagram](https://user-images.githubusercontent.com/81981552/124055582-27eba600-d9f2-11eb-8751-7cc8fe63a17c.jpeg)

## Application use
## Creation of package
To put a package into the database you need to make the method PUT with the following format:

*/fedex/packages/{user_email}*

This will registrate your package with an unique identifier, and will register you the customer to into the database.
It is important that the body of your request needs to look like this.

    {
        "name": " <Your name> ",
        "last_name": " <Your last name> ",
        "dimensions": " <The dimensions of the package, a number (Multiply the dimensions)> ",
        "weight": " <Weight of the package in kg, a number> ",
        "type": " <Type of the package> ",
        "origin": " <Origin city of the package> ",
        "destination": " <Destination city of the package> "
    }

After you register the package a notification will pop up in your email, this is a notification that the corporation sends you in order that you can receive information of your package.
Do not forget to accept this confirmation or we will be unable to inform you.

**The following parts are the job of an employee of the company:**

## Calculate the estimated price with the discounts that are available
To calculate the estimated price of a package within a season that contain a discount it is mandatory for the table to have an item with this structure:

    {
      "pk": " <season_id> ",
      "season_discount": " <Number> ",
      "season_type": " <What kind of season is, like spring>",
      "sk": <season_id>
    }   
    
With this done, is required to make the method PUT with the following format:

*/fedex/packages/{packageId}/customers/{customerId}/seasons/{seasonId}*

This will update the table adding the estimated price to pay.

## Change state of package
To change the state of a package to packaged, embarked, routed, arrived or delivered is required to make the method PUT with one of the following format:

*/fedex/packages/{packageId}/{stateName}*

This will change the state in the table and send the client an email with the information of the change. 

## Interaction with the customers website
To make possible for customers to track the state of their packages we create a website.
Once all the aplication is deployed, exists one more command that will create the website:

`./deployment.sh -w`

Once this is done you can access the website that is created in the S3 bucket with the name *fedex-customers-web*

NOTE: Is important to review the file index.html and change the url of the api gateway to the correct one, this happens because every use of this template will generate a new api and of course a new url.
