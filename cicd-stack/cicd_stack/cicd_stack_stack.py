from aws_cdk import (
    Stack,
    Duration,
    SecretValue,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    aws_ecr as ecr,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_codedeploy as codedeploy,
    # BD
    aws_rds as rds,
)
from constructs import Construct

class CicdStackStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ===========================================================================
        # Crear el rol de servicio para CodeDeploy en ECS
        code_deploy_role = iam.Role(
            self, "CodeDeployECSRole",
            assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com"),
            description="Rol de servicio para CodeDeploy en ECS",
        )

        # Agregar los permisos necesarios
        code_deploy_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AWSCodeDeployRoleForECS"))
        code_deploy_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("ElasticLoadBalancingFullAccess"))
        code_deploy_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonECS_FullAccess"))


        # ===========================================================================
        # Aqui inicia la definicion del ciclo CI.
        # ===========================================================================
        
        # Crear el repositorio ECR
        python_app_repo = ecr.Repository(
            self, 
            "PythonAppRepository",
            repository_name="python_app"
        )

        # Obtener la URI del repositorio
        repo_uri = python_app_repo.repository_uri

        # Imprimir la URI para confirmación (opcional)
        print(f"Repositorio ECR creado. URI: {repo_uri}")

        # Permisos adicionales opcionales: permite que otros servicios usen el repositorio
        python_app_repo.grant_pull_push(iam.ServicePrincipal("codebuild.amazonaws.com"))
        python_app_repo.grant_pull(iam.ServicePrincipal("ecs-tasks.amazonaws.com"))


        # Proyecto CodeBuild para construir y subir la imagen Docker
        codebuild_project = codebuild.PipelineProject(
            self, 
            "DockerBuildProject",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_6_0,
                privileged=True  # Requerido para comandos Docker
            ),
            environment_variables={
                "ECR_REPOSITORY_URI": codebuild.BuildEnvironmentVariable(value=python_app_repo.repository_uri),
                "AWS_REGION": codebuild.BuildEnvironmentVariable(value=self.region)
            },
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "pre_build": {
                        "commands": [
                            "aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY_URI"
                        ]
                    },
                    "build": {
                        "commands": [
                            "pip install -r requirements.txt",
                            "export FLASK_ENV=testing",
                            "set -e",
                            "pytest tests/",
                            "docker build -t python_app:latest .",
                            "docker tag python_app:latest $ECR_REPOSITORY_URI:latest"
                        ]
                    },
                    "post_build": {
                        "commands": [
                            "docker push $ECR_REPOSITORY_URI:latest",
                            "echo 'Image has been pushed to ECR'"
                        ]
                    }
                }
            })
        )

        # Permisos para CodeBuild para interactuar con ECR
        python_app_repo.grant_pull_push(codebuild_project.role)

        # Pipeline de CodePipeline
        pipeline = codepipeline.Pipeline(
            self, "ECRPipeline",
            pipeline_name="PythonAppECRPipeline"
        )

        # Agregar una etapa de origen (Source) para el repositorio de GitHub
        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="GitHub_Source",
            owner="DaGamez", # confirmar si es dagamez o yo puedo.
            repo="202415-devops-grupo9-compumundohipermegared",
            oauth_token=SecretValue.secrets_manager("github-token-cicd"), # NEceisto ser admin o owner.
            branch="main",
            # trigger=codepipeline_actions.GitHubSourceActionTrigger.WEBHOOK, # push contra main.
            output=source_output
        )
        pipeline.add_stage(
            stage_name="Source",
            actions=[source_action]
        )

        # Agregar una etapa de compilación (Build) que usa CodeBuild

        # Crear artefacto de salida de la construcción
        build_output = codepipeline.Artifact()


        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Docker_Build_and_Push",
            project=codebuild_project,
            input=source_output,
            outputs=[build_output], ## TO BD VERIFY ##
        )
        pipeline.add_stage(
            stage_name="Build",
            actions=[build_action]
        )

        
        # Crear un VPC
        vpc = ec2.Vpc(self, "MyVpc", max_azs=3)

        # Crear un grupo de seguridad que permite tráfico entrante y saliente desde y hacia internet
        security_group = ec2.SecurityGroup(self, "MySecurityGroup",
                                          vpc=vpc,
                                          description="Allow all inbound and outbound traffic",
                                          allow_all_outbound=True)  # Permitir todo el tráfico saliente
        security_group.add_ingress_rule(ec2.Peer.any_ipv4(), 
                                        ec2.Port.all_traffic(), 
                                        "Allow all inbound traffic from any IPv4 address")

        # Crear el Load Balancer
        lb = elbv2.ApplicationLoadBalancer(self, "MyLoadBalancer",
                                           vpc=vpc,
                                           security_group=security_group,
                                           internet_facing=True)

        # Crear el Target Group 1
        target_group_1 = elbv2.ApplicationTargetGroup(self, "TargetGroup1",
                                                      vpc=vpc,
                                                      target_type=elbv2.TargetType.IP,
                                                      protocol=elbv2.ApplicationProtocol.HTTP,
                                                      port=5000) # revisar helh check que no me acuerdo.,

        # Crear el Target Group 2
        target_group_2 = elbv2.ApplicationTargetGroup(self, "TargetGroup2",
                                                      vpc=vpc,
                                                      target_type=elbv2.TargetType.IP,
                                                      protocol=elbv2.ApplicationProtocol.HTTP,
                                                      port=5000) # revisar helh check que no me acuerdo.,

        # Crear los listeners para el Load Balancer y apuntamos al ambiente de test y de prod
        listener_production = lb.add_listener(
            "Listener80",
            port=80,
            open=True
        )
        listener_production.add_target_groups(
            "ProductionTargetGroup",
            target_groups=[target_group_1]
        )

        listener_test = lb.add_listener(
            "Listener8080",
            port=8080,
            open=True
        )
        listener_test.add_target_groups(
            "TestTargetGroup",
            target_groups=[target_group_2]
        )


        # Aqui vamos con la BD

        # Crear un grupo de seguridad específico para RDS
        db_security_group = ec2.SecurityGroup(
            self, "DatabaseSecurityGroup",
            vpc=vpc,
            description="Security group for RDS PostgreSQL",
            allow_all_outbound=True
        )

        # Permitir tráfico entrante desde el grupo de seguridad del servicio ECS
        db_security_group.add_ingress_rule(
            peer=security_group,
            connection=ec2.Port.tcp(5432),
            description="Allow PostgreSQL access from ECS tasks" # <-- El container estara com una task
        )

        # Crear la instancia de RDS PostgreSQL
        database = rds.DatabaseInstance(
            self, "Database",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_14
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[db_security_group],
            # credentials=rds.Credentials.from_secret(database_credentials),
            credentials=rds.Credentials.from_password(
                username="postgres",
                password=SecretValue.unsafe_plain_text("secret-database-password")  # No recomendado para producción (TODO: Revisar esto y mejroar)
            ),
            database_name="postgres",
            port=5432,
            allocated_storage=20,
            max_allocated_storage=100,
            publicly_accessible=False,
            deletion_protection=False  # Cambiar a True en producción
        )


        # Cluster fargate: Ver Actividad 4 – Creación de Task Definition y Cluster sobre AWS ECS

        # Cluster ECS para Fargate
        cluster = ecs.Cluster(self, "ClusterAppPython",
            vpc=vpc,
            cluster_name="cluster-app-python"
        )

        # Por si llegamos a neceistar autoescalado:
        # cluster.add_auto_scaling_group_capacity(
        #     "AutoScalingGroup",
        #     instance_type=ec2.InstanceType.of(
        #         ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
        #     ),
        #     desired_capacity=2
        # )



        # Definir la tarea para Fargate
        task_definition = ecs.FargateTaskDefinition(self, "TaskDef",
            memory_limit_mib=3072,
            cpu=1024
        )

        # Crear el rol de ejecución si es necesario
        task_execution_role = task_definition.obtain_execution_role()
        task_execution_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
        )

        # Definir el contenedor
        container = task_definition.add_container("ContainerAppPython",
            image=ecs.ContainerImage.from_registry(repo_uri), # URI donde tenemos nuetsra imagen docker.
            container_name="Container-app-python",
            environment={
                "FLASK_ENV": "production"
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="ContainerAppPythonLogs")
        )
        container.add_port_mappings(
            ecs.PortMapping(container_port=5000, host_port=5000, protocol=ecs.Protocol.TCP)
        )


        # Crear el servicio en ECS con el tipo de despliegue azul/verde
        ecs_service = ecs.FargateService(self, "ServiceAppPython",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1, #min instance en GCP
            security_groups=[security_group],
            assign_public_ip=True, # DNS publico.
            deployment_controller={
                "type": ecs.DeploymentControllerType.CODE_DEPLOY
            }
        )

        # Atachar el servicio al target group
        ecs_service.attach_to_application_target_group(target_group_1)

        ## AUQI INICIA LA ETAPA DE CD
        
        # Permitir que la pipeline haga el despliegue en ECS
        ecs_service.task_definition.task_role.add_to_policy(iam.PolicyStatement(
            actions=["ecs:UpdateService"],
            resources=["*"],
        ))

        # Etapa de despliegue a Fargate (ECS)
        deploy_action = codepipeline_actions.EcsDeployAction(
            action_name="DeployToECSFargate",
            service=ecs_service,
            input=build_output,  # Artefacto de salida de la construcción ## TO BE VERIFY ##
        )

        pipeline.add_stage(
            stage_name="Deploy",
            actions=[deploy_action],
        )


        # Crear el recurso de CodeDeploy para azul/verde
        deployment_group = codedeploy.EcsDeploymentGroup(self, "EcsDeploymentGroup",
            service=ecs_service,
            blue_green_deployment_config=codedeploy.EcsBlueGreenDeploymentConfig(
                blue_target_group=target_group_1, # 80
                green_target_group=target_group_2, # 8080
                listener=listener_production
            ),
            deployment_config=codedeploy.EcsDeploymentConfig.CANARY_10_PERCENT_5_MINUTES
        )

