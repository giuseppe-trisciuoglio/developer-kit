Amazon Bedrock examples using SDK for Java 2.x - AWS SDK for Java 2.x

Amazon Bedrock examples using SDK for Java 2.x - AWS SDK for Java 2.x

[Open PDF](http://https:%2F%2Fdocs.aws.amazon.com%2Fsdk-for-java%2Flatest%2Fdeveloper-guide%2Fjava_bedrock_code_examples.html/pdfs/sdk-for-java/latest/developer-guide/aws-sdk-java-dg-v2.pdf#java_bedrock_code_examples "Open PDF")

[Documentation](http://https:%2F%2Fdocs.aws.amazon.com%2Fsdk-for-java%2Flatest%2Fdeveloper-guide%2Fjava_bedrock_code_examples.html/index.html) [AWS SDK for Java](http://https:%2F%2Fdocs.aws.amazon.com%2Fsdk-for-java%2Flatest%2Fdeveloper-guide%2Fjava_bedrock_code_examples.html/sdk-for-java/index.html) [Developer Guide for version 2.x](http://https:%2F%2Fdocs.aws.amazon.com%2Fsdk-for-java%2Flatest%2Fdeveloper-guide%2Fjava_bedrock_code_examples.html/home.html)

[Actions](http://https:%2F%2Fdocs.aws.amazon.com%2Fsdk-for-java%2Flatest%2Fdeveloper-guide%2Fjava_bedrock_code_examples.html#actions)

# Amazon Bedrock examples using SDK for Java 2.x

The following code examples show you how to perform actions and implement common scenarios by using
the AWS SDK for Java 2.x with Amazon Bedrock.

_Actions_ are code excerpts from larger programs and must be run in context. While actions show you how to call individual service functions, you can see actions in context in their related scenarios.

Each example includes a link to the complete source code, where you can find
instructions on how to set up and run the code in context.

###### Topics

- [Actions](http://https:%2F%2Fdocs.aws.amazon.com%2Fsdk-for-java%2Flatest%2Fdeveloper-guide%2Fjava_bedrock_code_examples.html#actions)


## Actions

The following code example shows how to use `GetFoundationModel`.

**SDK for Java 2.x**

###### Note

There's more on GitHub. Find the complete example and learn how to set up and run in the
[AWS Code\
Examples Repository](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/bedrock#code-examples).


Get details about a foundation model using the synchronous Amazon Bedrock client.

```java

    /**
     * Get details about an Amazon Bedrock foundation model.
     *
     * @param bedrockClient   The service client for accessing Amazon Bedrock.
     * @param modelIdentifier The model identifier.
     * @return An object containing the foundation model's details.
     */
    public static FoundationModelDetails getFoundationModel(BedrockClient bedrockClient, String modelIdentifier) {
        try {
            GetFoundationModelResponse response = bedrockClient.getFoundationModel(
                    r -> r.modelIdentifier(modelIdentifier)
            );

            FoundationModelDetails model = response.modelDetails();

            System.out.println(" Model ID:                     " + model.modelId());
            System.out.println(" Model ARN:                    " + model.modelArn());
            System.out.println(" Model Name:                   " + model.modelName());
            System.out.println(" Provider Name:                " + model.providerName());
            System.out.println(" Lifecycle status:             " + model.modelLifecycle().statusAsString());
            System.out.println(" Input modalities:             " + model.inputModalities());
            System.out.println(" Output modalities:            " + model.outputModalities());
            System.out.println(" Supported customizations:     " + model.customizationsSupported());
            System.out.println(" Supported inference types:    " + model.inferenceTypesSupported());
            System.out.println(" Response streaming supported: " + model.responseStreamingSupported());

            return model;

        } catch (ValidationException e) {
            throw new IllegalArgumentException(e.getMessage());
        } catch (SdkException e) {
            System.err.println(e.getMessage());
            throw new RuntimeException(e);
        }
    }

```

Get details about a foundation model using the asynchronous Amazon Bedrock client.

```java

    /**
     * Get details about an Amazon Bedrock foundation model.
     *
     * @param bedrockClient   The async service client for accessing Amazon Bedrock.
     * @param modelIdentifier The model identifier.
     * @return An object containing the foundation model's details.
     */
    public static FoundationModelDetails getFoundationModel(BedrockAsyncClient bedrockClient, String modelIdentifier) {
        try {
            CompletableFuture<GetFoundationModelResponse> future = bedrockClient.getFoundationModel(
                    r -> r.modelIdentifier(modelIdentifier)
            );

            FoundationModelDetails model = future.get().modelDetails();

            System.out.println(" Model ID:                     " + model.modelId());
            System.out.println(" Model ARN:                    " + model.modelArn());
            System.out.println(" Model Name:                   " + model.modelName());
            System.out.println(" Provider Name:                " + model.providerName());
            System.out.println(" Lifecycle status:             " + model.modelLifecycle().statusAsString());
            System.out.println(" Input modalities:             " + model.inputModalities());
            System.out.println(" Output modalities:            " + model.outputModalities());
            System.out.println(" Supported customizations:     " + model.customizationsSupported());
            System.out.println(" Supported inference types:    " + model.inferenceTypesSupported());
            System.out.println(" Response streaming supported: " + model.responseStreamingSupported());

            return model;

        } catch (ExecutionException e) {
            if (e.getMessage().contains("ValidationException")) {
                throw new IllegalArgumentException(e.getMessage());
            } else {
                System.err.println(e.getMessage());
                throw new RuntimeException(e);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            System.err.println(e.getMessage());
            throw new RuntimeException(e);
        }
    }

```

- For API details, see
[GetFoundationModel](https://docs.aws.amazon.com/goto/SdkForJavaV2/bedrock-2023-04-20/GetFoundationModel)
in _AWS SDK for Java 2.x API Reference_.



The following code example shows how to use `ListFoundationModels`.

**SDK for Java 2.x**

###### Note

There's more on GitHub. Find the complete example and learn how to set up and run in the
[AWS Code\
Examples Repository](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/bedrock#code-examples).


List the available Amazon Bedrock foundation models using the synchronous Amazon Bedrock client.

```java

    /**
     * Lists Amazon Bedrock foundation models that you can use.
     * You can filter the results with the request parameters.
     *
     * @param bedrockClient The service client for accessing Amazon Bedrock.
     * @return A list of objects containing the foundation models' details
     */
    public static List<FoundationModelSummary> listFoundationModels(BedrockClient bedrockClient) {

        try {
            ListFoundationModelsResponse response = bedrockClient.listFoundationModels(r -> {});

            List<FoundationModelSummary> models = response.modelSummaries();

            if (models.isEmpty()) {
                System.out.println("No available foundation models in " + region.toString());
            } else {
                for (FoundationModelSummary model : models) {
                    System.out.println("Model ID: " + model.modelId());
                    System.out.println("Provider: " + model.providerName());
                    System.out.println("Name:     " + model.modelName());
                    System.out.println();
                }
            }

            return models;

        } catch (SdkClientException e) {
            System.err.println(e.getMessage());
            throw new RuntimeException(e);
        }
    }

```

List the available Amazon Bedrock foundation models using the asynchronous Amazon Bedrock client.

```java

    /**
     * Lists Amazon Bedrock foundation models that you can use.
     * You can filter the results with the request parameters.
     *
     * @param bedrockClient The async service client for accessing Amazon Bedrock.
     * @return A list of objects containing the foundation models' details
     */
    public static List<FoundationModelSummary> listFoundationModels(BedrockAsyncClient bedrockClient) {
        try {
            CompletableFuture<ListFoundationModelsResponse> future = bedrockClient.listFoundationModels(r -> {});

            List<FoundationModelSummary> models = future.get().modelSummaries();

            if (models.isEmpty()) {
                System.out.println("No available foundation models in " + region.toString());
            } else {
                for (FoundationModelSummary model : models) {
                    System.out.println("Model ID: " + model.modelId());
                    System.out.println("Provider: " + model.providerName());
                    System.out.println("Name:     " + model.modelName());
                    System.out.println();
                }
            }

            return models;

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            System.err.println(e.getMessage());
            throw new RuntimeException(e);
        } catch (ExecutionException e) {
            System.err.println(e.getMessage());
            throw new RuntimeException(e);
        }
    }

```

- For API details, see
[ListFoundationModels](https://docs.aws.amazon.com/goto/SdkForJavaV2/bedrock-2023-04-20/ListFoundationModels)
in _AWS SDK for Java 2.x API Reference_.



[Document Conventions](http://https:%2F%2Fdocs.aws.amazon.com%2Fsdk-for-java%2Flatest%2Fdeveloper-guide%2Fjava_bedrock_code_examples.html/general/latest/gr/docconventions.html)

AWS Batch

Amazon Bedrock Runtime

Did this page help you? - Yes

Thanks for letting us know we're doing a good job!

If you've got a moment, please tell us what we did right so we can do more of it.

Did this page help you? - No

Thanks for letting us know this page needs work. We're sorry we let you down.

If you've got a moment, please tell us how we can make the documentation better.