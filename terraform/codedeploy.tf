resource "aws_codedeploy_app" "ecs_app" {
  compute_platform = "ECS"
  name             = "python-app-deploy"
}

resource "aws_codedeploy_deployment_group" "ecs_deployment_group" {
  app_name               = aws_codedeploy_app.ecs_app.name
  deployment_group_name  = "ecs-deployment-group"
  service_role_arn      = aws_iam_role.code_deploy_role.arn

  deployment_config_name = "CodeDeployDefault.ECSAllAtOnce" 
  
  deployment_style {
    deployment_option = "WITH_TRAFFIC_CONTROL"
    deployment_type   = "BLUE_GREEN"
  }

  blue_green_deployment_config {
    deployment_ready_option {
      action_on_timeout = "CONTINUE_DEPLOYMENT"
    }

    terminate_blue_instances_on_deployment_success {
      action                           = "TERMINATE"
      termination_wait_time_in_minutes = 5
    }
  }

  ecs_service {
    cluster_name = aws_ecs_cluster.app_cluster.name
    service_name = aws_ecs_service.app_service.name
  }

  load_balancer_info {
    target_group_pair_info {
      prod_traffic_route {
        listener_arns = [aws_lb_listener.listener_production.arn]
      }

      target_group {
        name = aws_lb_target_group.target_group_1.name
      }

      target_group {
        name = aws_lb_target_group.target_group_2.name
      }
    }
  }
}